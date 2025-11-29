"""Tests for SymbolicMemoryStore."""

from akari.memory.models import MemoryChannelId
from akari.memory.symbolic_store import SymbolicMemoryStore


def test_symbolic_memory_write_and_query_by_metadata() -> None:
    store = SymbolicMemoryStore()

    store.write(
        channel=MemoryChannelId('notes'),
        record_id='r1',
        content='hello world',
        metadata={'topic': 'greeting', 'user': 'alice'},
    )
    store.write(
        channel=MemoryChannelId('notes'),
        record_id='r2',
        content='another note',
        metadata={'topic': 'other', 'user': 'bob'},
    )

    results = store.query(
        channel=MemoryChannelId('notes'),
        metadata_filters={'topic': 'greeting'},
    )
    assert len(results) == 1
    assert results[0].id == 'r1'


def test_symbolic_memory_query_text_contains() -> None:
    store = SymbolicMemoryStore()

    store.write(
        channel=MemoryChannelId('logs'),
        record_id='r1',
        content='Error: something went wrong',
    )
    store.write(
        channel=MemoryChannelId('logs'),
        record_id='r2',
        content='All good',
    )

    results = store.query(
        channel=MemoryChannelId('logs'),
        text_contains='error',
    )
    assert len(results) == 1
    assert results[0].id == 'r1'
