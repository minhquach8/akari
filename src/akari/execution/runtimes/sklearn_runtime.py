"""Runtime for sklearn models."""

from __future__ import annotations

from typing import Any

from akari.registry.specs import BaseSpec

from .base import ModelRuntime


class SklearnRuntime(ModelRuntime):
    """Execute a sklearn model by calling model.predict()."""

    def run(self, spec: BaseSpec, task_input: Any) -> Any:
        model = spec.binding

        if not hasattr(model, "predict"):
            raise TypeError(
                f"Spec {spec.id} does not have a sklearn-compatible binding"
            )

        try:
            # task_input should be list/array-like
            return model.predict(task_input)
        except Exception as e:
            raise RuntimeError(f"SklearnRuntime failed: {e}") from e
