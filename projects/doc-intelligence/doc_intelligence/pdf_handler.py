"""Doc Intelligence - PDF 文档解析"""

import os
from typing import List, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


class PDFHandler:
    """PDF 文档解析与文本提取"""

    def __init__(self):
        if fitz is None:
            raise ImportError("请安装 PyMuPDF: pip install pymupdf")

    def extract_text(self, file_path: str) -> str:
        """提取 PDF 全部文本"""
        doc = fitz.open(file_path)
        texts = []
        for page in doc:
            texts.append(page.get_text())
        doc.close()
        return "\n".join(texts)

    def extract_pages(self, file_path: str, start: int = 0, end: Optional[int] = None) -> List[str]:
        """提取指定页码的文本"""
        doc = fitz.open(file_path)
        texts = []
        end = end or len(doc)
        for i in range(start, min(end, len(doc))):
            texts.append(doc[i].get_text())
        doc.close()
        return texts

    def get_metadata(self, file_path: str) -> dict:
        """获取 PDF 元信息"""
        doc = fitz.open(file_path)
        meta = doc.metadata
        info = {
            "pages": len(doc),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "creation_date": meta.get("creationDate", ""),
        }
        doc.close()
        return info

    def to_markdown(self, file_path: str, output_path: Optional[str] = None) -> str:
        """PDF 转 Markdown"""
        doc = fitz.open(file_path)
        md_parts = []
        for i, page in enumerate(doc):
            text = page.get_text()
            md_parts.append(f"<!-- Page {i + 1} -->\n\n{text.strip()}")
        doc.close()
        md_content = "\n\n---\n\n".join(md_parts)
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
        return md_content

    def count_pages(self, file_path: str) -> int:
        """获取 PDF 页数"""
        doc = fitz.open(file_path)
        count = len(doc)
        doc.close()
        return count
