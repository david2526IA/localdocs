"""Transparent BM25-style lexical ranking with no remote services."""

from __future__ import annotations

import math
import re
from collections import Counter

TOKEN = re.compile(r"[\wáéíóúüñ]+", flags=re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def rank(query: str, documents: list[dict[str, object]], limit: int = 5) -> list[dict[str, object]]:
    """Score chunks with BM25; return the strongest source-backed passages."""
    terms = tokenize(query)
    if not terms or not documents:
        return []
    tokenized = [tokenize(str(item["content"])) for item in documents]
    total = len(tokenized)
    average_length = sum(len(item) for item in tokenized) / total
    document_frequency = Counter(term for tokens in tokenized for term in set(tokens))
    scored: list[dict[str, object]] = []
    for item, tokens in zip(documents, tokenized):
        frequencies = Counter(tokens)
        score = 0.0
        for term in terms:
            if not frequencies[term]:
                continue
            idf = math.log(1 + (total - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
            denominator = frequencies[term] + 1.5 * (1 - 0.75 + 0.75 * len(tokens) / max(average_length, 1))
            score += idf * frequencies[term] * 2.5 / denominator
        if score:
            scored.append({**item, "score": round(score, 4)})
    return sorted(scored, key=lambda item: float(item["score"]), reverse=True)[:limit]
