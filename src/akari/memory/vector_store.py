"""Vector memory store and simple embedding interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .models import MemoryChannelId


class EmbeddingFunction(ABC):
    """Interface for text embedding functions."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Convert text into a vector embedding."""
        raise NotImplementedError


class SimpleEmbeddingFunction(EmbeddingFunction):
    """Very simple embedding for tests and examples.

    This is deliberately trivial to avoid extra dependencies. It
    converts a string into a fixed-length vector of character counts.
    """

    def __init__(self, vocab: str = 'abcdefghijklmnopqrstuvwxyz ') -> None:
        self._vocab = vocab
        self._index = {ch: i for i, ch in enumerate(vocab)}

    def embed(self, text: str) -> List[float]:
        vector = [0.0] * len(self._vocab)
        for ch in text.lower():
            if ch in self._index:
                vector[self._index[ch]] += 1.0
        return vector


@dataclass
class VectorRecord:
    """Vector record for semantic search."""

    id: str
    channel: MemoryChannelId
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class VectorMemoryStore:
    """In-memory vector store with cosine similarity search."""

    def __init__(self, embedding_fn: EmbeddingFunction) -> None:
        self._embedding_fn = embedding_fn
        self._records_by_channel: Dict[MemoryChannelId, List[VectorRecord]] = {}

    # ---- Index ----------------------------------------------------------

    def index(
        self,
        channel: MemoryChannelId,
        record_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VectorRecord:
        embedding = self._embedding_fn.embed(text)
        record = VectorRecord(
            id=record_id,
            channel=channel,
            text=text,
            embedding=embedding,
            metadata=metadata or {},
        )
        self._records_by_channel.setdefault(channel, []).append(record)
        return record

    # ---- Search ---------------------------------------------------------

    def search(
        self,
        channel: MemoryChannelId,
        query_text: str,
        top_k: int = 5,
    ) -> List[Tuple[VectorRecord, float]]:
        """Search for most similar records to query_text in a channel.

        Returns a list of (record, similarity) sorted by similarity desc.
        """
        query_vec = self._embedding_fn.embed(query_text)
        records = self._records_by_channel.get(channel, [])
        scored: List[Tuple[VectorRecord, float]] = []

        for rec in records:
            sim = self._cosine_similarity(query_vec, rec.embedding)
            scored.append((rec, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
