"""Tests for MemorySubsystem with policy enforcement."""

from akari.memory.api import MemorySubsystem
from akari.memory.symbolic_store import SymbolicMemoryStore
from akari.memory.vector_store import SimpleEmbeddingFunction, VectorMemoryStore
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet


def _make_memory_with_policy() -> MemorySubsystem:
    rules = [
        PolicyRule(
            id="allow-sensitive-write",
            description="Allow writes to sensitive channel",
            subject_match="*",
            action="memory.write",
            resource_match="memory:sensitive",
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id="deny-sensitive-read",
            description="Deny read from sensitive channel",
            subject_match="*",
            action="memory.read",
            resource_match="memory:sensitive",
            effect=PolicyEffect.DENY,
        ),
    ]
    policy_set = PolicySet(name="memory-test", rules=rules, version="v1")
    engine = PolicyEngine(policy_set)

    symbolic = SymbolicMemoryStore()
    embedding_fn = SimpleEmbeddingFunction()
    vector_store = VectorMemoryStore(embedding_fn)

    return MemorySubsystem(
        symbolic_store=symbolic,
        vector_store=vector_store,
        policy_engine=engine,
        logger=None,
    )


def test_memory_policy_denies_read() -> None:
    memory = _make_memory_with_policy()

    # Write to sensitive channel (explicitly allowed by policy).
    rec = memory.write_symbolic(
        channel="sensitive",
        record_id="r1",
        content="top secret",
        subject="user:alice",
    )
    assert rec is not None

    # Read should be denied and return empty list.
    results = memory.query_symbolic(
        channel="sensitive",
        subject="user:alice",
    )
    assert results == []
