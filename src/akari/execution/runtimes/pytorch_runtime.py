"""Runtime for PyTorch models."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from akari.registry.specs import BaseSpec

from .base import ModelRuntime


class PytorchRuntime(ModelRuntime):
    """Execute a PyTorch model or callable using torch.no_grad()."""

    def run(self, spec: BaseSpec, task_input: Any) -> Any:
        """
        Execute the PyTorch binding in `spec` on the given input.

        Args:
            spec:
                A spec whose `binding` is either a torch.nn.Module
                hoặc một callable dùng torch.
            task_input:
                Dữ liệu đầu vào: list / numpy array / torch.Tensor.

        Returns:
            Output dưới dạng numpy array (nếu là tensor) hoặc giữ nguyên kiểu khác.
        """
        model = spec.binding

        # Chuẩn hoá input thành tensor
        if isinstance(task_input, torch.Tensor):
            x = task_input
        else:
            x = torch.as_tensor(task_input)

        try:
            # Case 1: torch.nn.Module
            if isinstance(model, torch.nn.Module):
                model.eval()
                with torch.no_grad():
                    out = model(x)
            else:
                # Case 2: callable wrapper
                with torch.no_grad():
                    out = model(x)

            # Đưa tensor về CPU numpy cho thống nhất
            if isinstance(out, torch.Tensor):
                out = out.detach().cpu().numpy()

            if isinstance(out, np.ndarray):
                return out

            return out
        except Exception as e:
            # Giữ style giống SklearnRuntime
            raise RuntimeError(f"PytorchRuntime failed: {e}") from e
