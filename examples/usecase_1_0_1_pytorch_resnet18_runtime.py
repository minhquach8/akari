"""Use Case 1.0.1 – PyTorch ResNet18 runtime."""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec

try:
    from torchvision.models import resnet18
except Exception:  # pragma: no cover - optional dep
    resnet18 = None


def build_resnet18(num_classes: int = 1000) -> Any:
    if resnet18 is None:
        raise RuntimeError(
            "torchvision is not available. Install torchvision to run this example."
        )
    model = resnet18(weights=None, num_classes=num_classes)
    return model


def main() -> None:
    print("=== Use Case 1.0.1 – PyTorch ResNet18 runtime ===\n")

    if resnet18 is None:
        print("torchvision is not installed. Skipping ResNet18 example.")
        return

    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()

    model = build_resnet18(num_classes=1000)

    spec = ModelSpec(
        id="model:resnet18",
        name="ResNet18 classifier",
        runtime="pytorch",
        binding=model,
        tags={"demo", "pytorch", "resnet18"},
        metadata={},
    )
    registry.register(spec)
    print("Registered model 'model:resnet18' with runtime='pytorch'.")

    # Dummy input: batch size 1, 3x224x224
    x = np.random.rand(1, 3, 224, 224).astype("float32")

    task = Task(
        id="task:resnet18:dummy",
        subject="user:demo",
        workspace="workspace:vision",
        target_id="model:resnet18",
        input=x,
    )

    result = executor.run(task)
    print(f"\nTask status : {result.status}")
    print(f"Output type : {type(result.output)}")
    print(f"Output shape: {getattr(result.output, 'shape', None)}")

    print("\nResNet18 runtime example completed.")


if __name__ == "__main__":
    main()
