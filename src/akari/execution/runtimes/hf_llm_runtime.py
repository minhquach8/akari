"""Runtime for HuggingFace LLM / text pipelines."""

from __future__ import annotations

from typing import Any

from akari.registry.specs import BaseSpec

from .base import ModelRuntime


class HuggingFaceLLMRuntime(ModelRuntime):
    """Execute a HuggingFace pipeline or LLM-like callable.

    This runtime expects `spec.binding` to be a callable, typically a
    `transformers.pipeline` instance, that accepts `task_input` and returns
    a HuggingFace-style output (list[dict] or string).
    """

    runtime_name = "hf-llm"

    def run(self, spec: BaseSpec, task_input: Any) -> Any:
        """
        Execute the HuggingFace binding on the given input.

        Args:
            spec:
                Spec whose `binding` is a HF pipeline / callable.
            task_input:
                Input text (string) hoặc list các string.

        Returns:
            Whatever the underlying pipeline returns (thường là list[dict] hoặc str).
        """
        llm = spec.binding

        if not callable(llm):
            raise TypeError(
                f"Spec {spec.id} does not have a callable HuggingFace binding"
            )

        try:
            return llm(task_input)
        except Exception as e:
            raise RuntimeError(f"HuggingFaceLLMRuntime failed: {e}") from e
