"""
Use Case 0.3.3 – Task failure handling.

Demonstrates how TaskExecutor deals with runtime failures:
- A callable tool that raises an exception.
- The resulting Task and TaskResult show FAILED status and error message.
"""

from __future__ import annotations

from akari import Kernel
from akari.execution.task import Task, TaskStatus
from akari.registry.specs import ToolSpec


def always_fail() -> None:
    """A tool that always raises an exception."""
    raise RuntimeError("Intentional failure for demo")


def main() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    failing_tool = ToolSpec(
        id="tool:always_fail",
        name="Always fail tool",
        runtime="callable",
        binding=always_fail,
        tags={"demo", "failure"},
    )
    registry.register(failing_tool)

    task = Task(
        id="task:failure:demo",
        subject="user:demo",
        target_id="tool:always_fail",
        input={},  # no args
    )

    executor = kernel.get_executor()
    result = executor.run(task)

    print("=== Use Case 0.3.3 – Task failure handling ===\n")
    print("Task status:", task.status.value)
    print("Result status:", result.status.value)
    print("Error:", result.error)

    assert task.status is TaskStatus.FAILED


if __name__ == "__main__":
    main()
