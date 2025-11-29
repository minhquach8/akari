"""Use Case 1.0.0 – Boot Kernel from akari.yml config."""

from __future__ import annotations

import os
from typing import Any, Dict

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec


def ensure_artifacts_dirs() -> None:
    os.makedirs("artifacts/config_demo", exist_ok=True)


def build_kernel_from_config() -> Kernel:
    ensure_artifacts_dirs()
    # Kernel will read observability.log_* and observability.run_* from akari.yml
    return Kernel.from_config("akari.yml")


def main() -> None:
    print("=== Use Case 1.0.0 – Kernel.from_config ===\n")

    kernel = build_kernel_from_config()
    registry = kernel.get_registry()
    executor = kernel.get_executor()
    logger = kernel.get_logger()
    run_store = kernel.get_run_store()

    print(f"Logger backend type : {type(logger).__name__}")
    print(f"Run-store backend   : {type(run_store).__name__}")

    # Register a simple callable model
    def add_one(x: int) -> int:
        return x + 1

    spec = ModelSpec(
        id="model:add_one",
        name="Add one",
        runtime="callable",
        binding=add_one,
        tags={"demo", "config"},
        metadata={},
    )
    registry.register(spec)

    task = Task(
        id="task:add_one",
        subject="user:config-demo",
        workspace="workspace:config-demo",
        target_id="model:add_one",
        input=41,
    )

    result = executor.run(task)
    print(f"\nTask status : {result.status}")
    print(f"Task output : {result.output}")

    print(
        "\nYou should now see JSONL logs and JSON run files under artifacts/config_demo "
        "according to akari.yml."
    )

    print("\nKernel.from_config demo completed.")


if __name__ == "__main__":
    main()
