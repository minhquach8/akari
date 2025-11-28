"""
Use Case 0.3.1 – Task execution with CallableRuntime.

This example shows:

1. Register a simple callable tool.
2. Create a Task targeting the tool.
3. Execute the Task via Kernel.executor.
"""

from __future__ import annotations

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ToolSpec


def multiply(a: int, b: int) -> int:
    """Simple multiply function used by the callable tool."""
    return a * b


def main() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    # Register tool.
    tool_spec = ToolSpec(
        id="tool:multiply",
        name="Multiply two numbers",
        runtime="callable",
        binding=multiply,
        tags={"demo", "math"},
    )
    registry.register(tool_spec)

    # Build task.
    task = Task(
        id="task:multiply:demo",
        subject="user:demo",
        target_id="tool:multiply",
        input={"a": 4, "b": 5},
    )

    executor = kernel.get_executor()
    result = executor.run(task)

    print("=== Use Case 0.3.1 – CallableRuntime ===\n")
    print("Task status:", task.status.value)
    print("Result status:", result.status.value)
    print("Output:", result.output)


if __name__ == "__main__":
    main()
