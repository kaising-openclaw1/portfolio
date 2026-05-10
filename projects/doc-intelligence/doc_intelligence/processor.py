"""Doc Intelligence - 核心文档处理器"""

import os
from typing import Optional, Dict, Any, List

from .pdf_handler import PDFHandler
from .docx_handler import DocxHandler
from .keywords import KeywordEngine
from .llm_client import LLMClient


class DocumentProcessor:
    """统一文档处理入口：摘要、翻译、转换、关键词提取"""

    SUPPORTED_FORMATS = {".pdf", ".docx", ".md", ".txt"}

    def __init__(
        self,
        llm_api_key: Optional[str] = None,
        llm_base_url: str = "https://api.deepseek.com/v1",
        llm_model: str = "deepseek-chat",
    ):
        self.pdf = PDFHandler()
        self.docx = DocxHandler()
        self.keywords = KeywordEngine()
        self.llm = LLMClient(
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model,
        )

    def _read_file(self, file_path: str) -> str:
        """读取文档文本"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return self.pdf.extract_text(file_path)
        elif ext == ".docx":
            return self.docx.extract_text(file_path)
        elif ext in (".md", ".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            raise ValueError(f"不支持的格式: {ext}，支持 {self.SUPPORTED_FORMATS}")

    def summarize(self, file_path: str, max_length: int = 500) -> str:
        """生成文档摘要"""
        text = self._read_file(file_path)
        # 长文档分段处理
        if len(text) > 8000:
            chunks = [text[i:i+8000] for i in range(0, len(text), 8000)]
            chunk_summaries = [self.llm.summarize(c, max_length=max_length // len(chunks)) for c in chunks]
            return self.llm.summarize("\n".join(chunk_summaries), max_length=max_length)
        return self.llm.summarize(text, max_length=max_length)

    def translate(self, file_path: str, target_lang: str = "en") -> str:
        """翻译文档"""
        text = self._read_file(file_path)
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            translations = [self.llm.translate(c, target_lang) for c in chunks]
            return "\n\n".join(translations)
        return self.llm.translate(text, target_lang)

    def extract_keywords(self, file_path: str, top_k: int = 10, method: str = "hybrid") -> List[str]:
        """提取关键词"""
        text = self._read_file(file_path)
        if method == "tfidf":
            return self.keywords.extract_tfidf(text, top_k)
        elif method == "textrank":
            return self.keywords.extract_textrank(text, top_k)
        elif method == "llm":
            return self.llm.extract_keywords(text, top_k)
        else:  # hybrid
            return self.keywords.extract_hybrid(text, top_k)

    def convert(self, file_path: str, output_format: str = "markdown", output_dir: Optional[str] = None) -> str:
        """格式转换"""
        ext = os.path.splitext(file_path)[1].lower()
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        if output_format == "markdown":
            out_path = os.path.join(output_dir, f"{base_name}.md")
            if ext == ".pdf":
                content = self.pdf.to_markdown(file_path, out_path)
            elif ext == ".docx":
                content = self.docx.to_markdown(file_path, out_path)
            elif ext in (".md", ".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)
            return out_path
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def batch_process(
        self,
        input_dir: str,
        operations: List[str],
        output_dir: str,
        file_extensions: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """批量处理文档"""
        os.makedirs(output_dir, exist_ok=True)
        extensions = set(file_extensions or self.SUPPORTED_FORMATS)
        results = []

        for filename in os.listdir(input_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in extensions:
                continue
            file_path = os.path.join(input_dir, filename)
            result = {"file": filename, "operations": {}}

            for op in operations:
                try:
                    if op == "summarize":
                        result["operations"]["summarize"] = self.summarize(file_path)
                    elif op == "keywords":
                        result["operations"]["keywords"] = self.extract_keywords(file_path)
                    elif op == "convert":
                        result["operations"]["convert"] = self.convert(file_path, output_dir=output_dir)
                except Exception as e:
                    result["operations"][op] = f"错误: {str(e)}"

            results.append(result)

        return results
