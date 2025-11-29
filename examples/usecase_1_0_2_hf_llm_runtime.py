"""Use Case 1.0.2 – HuggingFace LLM runtime.

This example registers a HF summarisation pipeline as a model with
`runtime="hf-llm"` and executes it via TaskExecutor.
"""

from __future__ import annotations

from typing import Any, Dict, List

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec

try:
    from transformers import pipeline  # type: ignore[assignment]
except Exception:  # pragma: no cover - optional dependency
    pipeline = None


def build_summariser() -> Any:
    if pipeline is None:
        raise RuntimeError(
            "transformers is not available. Install 'transformers' to run this example."
        )
    # Dùng model summarisation mặc định (HF sẽ chọn cho bạn).
    summariser = pipeline("summarization")
    return summariser


def main() -> None:
    print("=== Use Case 1.0.2 – HuggingFace LLM runtime ===\n")

    if pipeline is None:
        print("transformers is not installed. Skipping HF LLM example.")
        return

    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()

    summariser = build_summariser()

    spec = ModelSpec(
        id="model:hf_summariser",
        name="HF text summariser",
        runtime="hf-llm",
        binding=summariser,
        tags={"demo", "hf", "summarisation"},
        metadata={},
    )
    registry.register(spec)
    print("Registered model 'model:hf_summariser' with runtime='hf-llm'.")

    long_text = (
        "AKARI is an AI control-plane kernel designed to orchestrate models, "
        "agents, tools, memory and policies with strong guarantees around "
        "observability and safety. It provides a small, stable kernel with a "
        "flexible userland, making cross-framework workflows reproducible and "
        "controllable."
    )

    task = Task(
        id="task:hf:summarise",
        subject="user:demo",
        workspace="workspace:nlp",
        target_id="model:hf_summariser",
        input=long_text,
    )

    result = executor.run(task)
    print(f"\nTask status: {result.status}")

    output = result.output
    print("\nRaw HF output:")
    print(output)

    # Thông thường summarisation pipeline trả về list[{"summary_text": "..."}]
    if isinstance(output, list) and output:
        first: Dict[str, Any] = output[0]
        summary = first.get("summary_text", "")
        print("\nSummary:")
        print(summary)

    print("\nHF LLM runtime example completed.")


if __name__ == "__main__":
    main()
