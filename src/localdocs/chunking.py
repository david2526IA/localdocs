"""Deterministic, dependency-free text chunking."""

from __future__ import annotations


def chunk_text(text: str, size: int = 140, overlap: int = 30) -> list[str]:
    """Split text by words while retaining enough context between chunks."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("size must be positive and overlap must be smaller than size")
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = size - overlap
    for start in range(0, len(words), step):
        chunk = words[start : start + size]
        if not chunk:
            break
        chunks.append(" ".join(chunk))
        if start + size >= len(words):
            break
    return chunks
