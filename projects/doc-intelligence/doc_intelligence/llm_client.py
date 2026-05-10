"""Doc Intelligence - LLM API 客户端（兼容 OpenAI 接口）"""

import json
import os
from typing import Optional, List, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMClient:
    """统一 LLM API 客户端，支持 OpenAI / DeepSeek / 通义千问 等"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        timeout: int = 60,
    ):
        self.model = model
        self.timeout = timeout
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")

        if OpenAI is None:
            raise ImportError(
                "请安装 openai 库: pip install openai"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """发送对话请求，返回文本响应"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def summarize(self, text: str, max_length: int = 500) -> str:
        """生成文本摘要"""
        prompt = (
            f"请为以下文本生成简明摘要，不超过 {max_length} 字。"
            f"摘要应涵盖核心要点，使用中文输出。\n\n{text}"
        )
        return self.chat([
            {"role": "system", "content": "你是一个专业的文档摘要助手。"},
            {"role": "user", "content": prompt},
        ], max_tokens=max_length + 200)

    def translate(self, text: str, target_lang: str = "en") -> str:
        """翻译文本"""
        lang_map = {
            "en": "英语",
            "zh": "中文",
            "ja": "日语",
            "ko": "韩语",
            "fr": "法语",
            "de": "德语",
            "es": "西班牙语",
        }
        target_name = lang_map.get(target_lang, target_lang)
        prompt = (
            f"请将以下文本翻译成{target_name}。保持专业术语准确，"
            f"语义流畅。只输出翻译结果，不要添加解释。\n\n{text}"
        )
        return self.chat([
            {"role": "system", "content": "你是一个专业的多语言翻译助手。"},
            {"role": "user", "content": prompt},
        ], max_tokens=len(text) * 2 + 500)

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        prompt = (
            f"请从以下文本中提取 {top_k} 个最重要的关键词或短语，"
            f"只返回关键词列表，用逗号分隔，不要编号。\n\n{text}"
        )
        result = self.chat([
            {"role": "system", "content": "你是一个关键词提取专家。"},
            {"role": "user", "content": prompt},
        ], max_tokens=200)
        keywords = [k.strip() for k in result.split(",") if k.strip()]
        return keywords[:top_k]

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """情感分析"""
        prompt = (
            f"请分析以下文本的情感倾向，返回 JSON 格式：\n"
            f'{{"sentiment": "positive/negative/neutral", '
            f'"confidence": 0.0-1.0, "key_emotions": ["情绪1", "情绪2"]}}\n\n{text}'
        )
        result = self.chat([
            {"role": "system", "content": "你是一个情感分析专家，返回纯JSON。"},
            {"role": "user", "content": prompt},
        ], max_tokens=200)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"sentiment": "unknown", "confidence": 0.0, "key_emotions": []}
