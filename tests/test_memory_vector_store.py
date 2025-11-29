"""Tests for VectorMemoryStore and simple semantic search."""

from akari.memory.models import MemoryChannelId
from akari.memory.vector_store import SimpleEmbeddingFunction, VectorMemoryStore


def test_vector_memory_search_ranking() -> None:
    embedding_fn = SimpleEmbeddingFunction()
    store = VectorMemoryStore(embedding_fn)

    channel = MemoryChannelId('docs')
    store.index(channel, 'r1', 'apple orange banana', metadata={'label': 'fruit'})
    store.index(channel, 'r2', 'car bus train', metadata={'label': 'vehicle'})
    store.index(channel, 'r3', 'apple pie recipe', metadata={'label': 'food'})

    # Query about apple should rank fruit-related texts higher.
    results = store.search(channel, 'apple', top_k=3)
    ids_in_order = [rec.id for rec, _score in results]

    # Ensure r1 or r3 appears before r2.
    assert ids_in_order[0] in {'r1', 'r3'}
    assert 'r2' in ids_in_order
