"""Use Case 0.5.1 – Symbolic memory write and query."""

from __future__ import annotations

from akari import Kernel


def main() -> None:
    kernel = Kernel()
    memory = kernel.get_memory()
    assert memory is not None

    print("=== Use Case 0.5.1 – Symbolic memory write/query ===\n")

    # Write several notes into "notes" channel.
    memory.write_symbolic(
        channel="notes",
        record_id="n1",
        content="Remember to review AKARI design.",
        subject="user:alice",
        metadata={"topic": "akari", "priority": "high"},
    )
    memory.write_symbolic(
        channel="notes",
        record_id="n2",
        content="Buy milk and bread.",
        subject="user:alice",
        metadata={"topic": "shopping", "priority": "low"},
    )
    memory.write_symbolic(
        channel="notes",
        record_id="n3",
        content="Read paper on explainability.",
        subject="user:bob",
        metadata={"topic": "xai", "priority": "medium"},
    )

    # Query notes by metadata.
    results = memory.query_symbolic(
        channel="notes",
        subject="user:alice",
        metadata_filters={"topic": "akari"},
    )
    print("Query by metadata (topic=akari):")
    for rec in results:
        print(f"  {rec.id}: {rec.content}")

    # Query by text substring.
    results2 = memory.query_symbolic(
        channel="notes",
        subject="user:alice",
        text_contains="paper",
    )
    print("\nQuery by text_contains='paper':")
    for rec in results2:
        print(f"  {rec.id}: {rec.content}")


if __name__ == "__main__":
    main()
