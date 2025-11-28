"""Use Case 0.4.2 – Policy: deny multiply tool."""

from __future__ import annotations

from akari.execution.executor import TaskExecutor
from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.callable_runtime import CallableRuntime
from akari.execution.task import Task, TaskStatus
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ToolSpec


def multiply(a: int, b: int) -> int:
    return a * b


def main() -> None:
    registry = IdentityRegistry()

    tool = ToolSpec(
        id="tool:multiply",
        name="Multiply",
        runtime="callable",
        binding=multiply,
    )
    registry.register(tool)

    runtime_registry = RuntimeRegistry()
    runtime_registry.register("callable", CallableRuntime())

    rules = [
        PolicyRule(
            id="deny-multiply",
            description="Deny use of multiply tool for everyone",
            subject_match="*",
            action="tool.invoke",
            resource_match="tool:multiply",
            effect=PolicyEffect.DENY,
        )
    ]
    policy_set = PolicySet(name="demo", rules=rules, version="v1")
    engine = PolicyEngine(policy_set)

    executor = TaskExecutor(
        registry=registry,
        runtime_registry=runtime_registry,
        policy_engine=engine,
    )

    task = Task(
        id="task:multiply:policy-demo",
        subject="user:demo",
        target_id="tool:multiply",
        input={"a": 3, "b": 4},
    )

    result = executor.run(task)

    print("=== Use Case 0.4.2 – Policy deny multiply tool ===\n")
    print("Task status:", task.status.value)
    print("Result status:", result.status.value)
    print("Error:", result.error)
    assert task.status is TaskStatus.FAILED


if __name__ == "__main__":
    main()
