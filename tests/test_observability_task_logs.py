"""Tests for task logging via InMemoryLogStore."""

from akari import Kernel
from akari.execution.task import Task, TaskStatus
from akari.observability.logging import InMemoryLogStore
from akari.registry.specs import ToolSpec


def test_task_logging_sequence() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()
    log_store = kernel.get_logger()
    assert isinstance(log_store, InMemoryLogStore)

    def add(a: int, b: int) -> int:
        return a + b

    tool = ToolSpec(
        id="tool:add",
        name="Add",
        runtime="callable",
        binding=add,
    )
    registry.register(tool)

    task = Task(
        id="task:add:1",
        subject="user:test",
        target_id="tool:add",
        input={"a": 1, "b": 2},
    )

    result = executor.run(task)

    assert task.status is TaskStatus.COMPLETED
    assert result.output == 3

    events = log_store.list_events()
    types = [e.event_type for e in events]

    # We expect at least created, started, completed in order.
    created_idx = types.index("task.created")
    started_idx = types.index("task.started")
    completed_idx = types.index("task.completed")

    assert created_idx < started_idx < completed_idx
