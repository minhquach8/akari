"""Use Case 0.5.2 – Vector memory semantic search."""

from __future__ import annotations

from akari import Kernel


def main() -> None:
    kernel = Kernel()
    memory = kernel.get_memory()
    assert memory is not None

    print("=== Use Case 0.5.2 – Vector semantic search ===\n")

    # Index a few short texts into vector memory.
    memory.index_vector(
        channel="docs",
        record_id="d1",
        text="Deep learning for image classification",
        subject="user:alice",
        metadata={"tag": "cv"},
    )
    memory.index_vector(
        channel="docs",
        record_id="d2",
        text="Reinforcement learning and control",
        subject="user:alice",
        metadata={"tag": "rl"},
    )
    memory.index_vector(
        channel="docs",
        record_id="d3",
        text="Explainable AI and model interpretability",
        subject="user:alice",
        metadata={"tag": "xai"},
    )

    # Search for something about explainability.
    results = memory.search_vector(
        channel="docs",
        query_text="interpretability of models",
        subject="user:alice",
        top_k=3,
    )

    print("Search results for 'interpretability of models':")
    for rec, score in results:
        print(f"  {rec.id} (score={score:.3f}): {rec.text}")


if __name__ == "__main__":
    main()
