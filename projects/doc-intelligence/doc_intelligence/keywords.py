"""Doc Intelligence - 关键词提取引擎"""

import re
from typing import List, Optional
from collections import Counter


class KeywordEngine:
    """双引擎关键词提取：TF-IDF + TextRank"""

    # 中文停用词（核心集）
    STOP_WORDS = set([
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
        "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
        "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "但",
        "而", "及", "与", "或", "等", "被", "把", "从", "向", "对", "于",
        "以", "为", "之", "其", "此", "若", "如", "该", "并", "且", "则",
        "is", "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "this", "that", "it", "be", "are",
        "was", "were", "been", "has", "have", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "can", "not",
    ])

    def extract_tfidf(self, text: str, top_k: int = 10) -> List[str]:
        """基于词频-逆文档频率的关键词提取"""
        words = self._tokenize(text)
        freq = Counter(w for w in words if w not in self.STOP_WORDS and len(w) > 1)
        return [w for w, _ in freq.most_common(top_k)]

    def extract_textrank(self, text: str, top_k: int = 10, window: int = 5) -> List[str]:
        """基于 TextRank 算法的关键词提取（简化版）"""
        words = [w for w in self._tokenize(text) if w not in self.STOP_WORDS and len(w) > 1]
        word_set = list(set(words))
        scores = {w: 1.0 for w in word_set}

        # 构建共现图
        cooccurrence = {w: set() for w in word_set}
        for i in range(len(words)):
            for j in range(i + 1, min(i + window, len(words))):
                if words[i] != words[j]:
                    cooccurrence[words[i]].add(words[j])
                    cooccurrence[words[j]].add(words[i])

        # PageRank 迭代
        damping = 0.85
        for _ in range(20):
            new_scores = {}
            for word in word_set:
                rank_sum = sum(
                    scores[nb] / len(cooccurrence[nb])
                    for nb in cooccurrence[word] if cooccurrence[nb]
                )
                new_scores[word] = (1 - damping) + damping * rank_sum
            scores = new_scores

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in ranked[:top_k]]

    def extract_hybrid(self, text: str, top_k: int = 10) -> List[str]:
        """混合 TF-IDF 和 TextRank 结果"""
        tfidf = self.extract_tfidf(text, top_k)
        textrank = self.extract_textrank(text, top_k)
        combined = []
        seen = set()
        for w in tfidf + textrank:
            if w not in seen:
                combined.append(w)
                seen.add(w)
        return combined[:top_k]

    def _tokenize(self, text: str) -> List[str]:
        """简单分词：中文按字/词边界，英文按空格"""
        try:
            import jieba
            return list(jieba.cut(text))
        except ImportError:
            # 降级：简单正则分词
            return re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
