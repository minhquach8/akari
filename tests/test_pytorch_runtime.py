"""Tests for PytorchRuntime integration with TaskExecutor."""

import numpy as np
import pytest
import torch
import torch.nn as nn

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec

pytest.importorskip("torch")  # Skip toàn bộ file nếu chưa cài torch.


def test_pytorch_runtime_linear_model() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()

    # Simple linear model: y = Wx, bias=False để dễ kiểm soát.
    model = nn.Linear(4, 1, bias=False)
    with torch.no_grad():
        model.weight.fill_(1.0)  # mọi hệ số = 1 → y = sum(x)

    spec = ModelSpec(
        id="model:pytorch_linear",
        name="Simple PyTorch linear",
        runtime="pytorch",
        binding=model,
        tags={"demo", "pytorch"},
        metadata={},
    )
    registry.register(spec)

    # Input shape (1, 4)
    x = np.array([[1.0, 2.0, 3.0, 4.0]], dtype=np.float32)
    task = Task(
        id="task:pytorch:linear",
        subject="user:test",
        workspace="workspace:test",
        target_id="model:pytorch_linear",
        input=x,
    )

    result = executor.run(task)

    assert result.status == "completed"
    out = result.output
    # out dự kiến là numpy array, reshape để lấy scalar.
    value = float(np.asarray(out).reshape(-1)[0])
    assert pytest.approx(value, rel=1e-5) == 10.0  # 1+2+3+4
