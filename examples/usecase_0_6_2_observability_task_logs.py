"""Use Case 0.6.2 – Task logs via Kernel logger."""

from __future__ import annotations

from akari import Kernel
from akari.execution.task import Task
from akari.observability.logging import InMemoryLogStore
from akari.registry.specs import ToolSpec


def add(a: int, b: int) -> int:
    return a + b


def main() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    executor = kernel.get_executor()
    log_store = kernel.get_logger()
    assert isinstance(log_store, InMemoryLogStore)

    tool = ToolSpec(
        id="tool:add",
        name="Add two numbers",
        runtime="callable",
        binding=add,
    )
    registry.register(tool)

    task = Task(
        id="task:add:demo",
        subject="user:demo",
        target_id="tool:add",
        input={"a": 10, "b": 32},
    )

    result = executor.run(task)

    print("=== Use Case 0.6.2 – Task logs ===\n")
    print("Result:", result.output)
    print("\nLogged events:")
    for event in log_store.list_events():
        print(
            f"- {event.timestamp.isoformat()} "
            f"{event.event_type} "
            f"(subject={event.subject}, task_id={event.task_id})"
        )


if __name__ == "__main__":
    main()
