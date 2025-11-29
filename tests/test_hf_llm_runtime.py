"""Tests for HuggingFaceLLMRuntime integration with TaskExecutor."""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec

transformers = pytest.importorskip("transformers")
from transformers import pipeline  # type: ignore[assignment]


def test_hf_llm_runtime_sentiment_pipeline() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()

    # Use a small / default sentiment-analysis pipeline.
    # HF sẽ tự tải model thích hợp (CPU-only is fine).
    sentiment = pipeline("sentiment-analysis")

    spec = ModelSpec(
        id="model:hf_sentiment",
        name="HF sentiment-analysis pipeline",
        runtime="hf-llm",
        binding=sentiment,
        tags={"demo", "hf", "sentiment"},
        metadata={},
    )
    registry.register(spec)

    task = Task(
        id="task:hf:sentiment",
        subject="user:test",
        workspace="workspace:test",
        target_id="model:hf_sentiment",
        input="AKARI is an excellent control-plane for AI workloads.",
    )

    result = executor.run(task)

    assert result.status == "completed"
    output = result.output

    # Sentiment pipeline normally returns list[dict[label, score, ...]]
    assert isinstance(output, list)
    assert len(output) >= 1
    first: Dict[str, Any] = output[0]
    assert "label" in first
    assert "score" in first
