"""Use Case 0.5.3 – Policy denies memory read from sensitive channel."""

from __future__ import annotations

from akari.memory.api import MemorySubsystem
from akari.memory.symbolic_store import SymbolicMemoryStore
from akari.memory.vector_store import SimpleEmbeddingFunction, VectorMemoryStore
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet


def build_memory_with_policy() -> MemorySubsystem:
    rules = [
        PolicyRule(
            id="allow-sensitive-write",
            description="Allow writes to sensitive memory channel",
            subject_match="*",
            action="memory.write",
            resource_match="memory:sensitive",
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id="deny-sensitive-read",
            description="Deny reads from sensitive memory channel",
            subject_match="*",
            action="memory.read",
            resource_match="memory:sensitive",
            effect=PolicyEffect.DENY,
        ),
    ]
    policy_set = PolicySet(name="demo", rules=rules, version="v1")
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


def main() -> None:
    memory = build_memory_with_policy()

    print("=== Use Case 0.5.3 – Memory deny read ===\n")

    # Write to sensitive channel.
    rec = memory.write_symbolic(
        channel="sensitive",
        record_id="s1",
        content="Very confidential data",
        subject="user:alice",
    )
    print("Write to 'sensitive' channel result:", "OK" if rec else "DENIED")

    # Attempt to read back from sensitive channel.
    results = memory.query_symbolic(
        channel="sensitive",
        subject="user:alice",
    )
    print("Read from 'sensitive' channel returned", len(results), "records")


if __name__ == "__main__":
    main()
