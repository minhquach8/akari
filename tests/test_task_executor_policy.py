"""Tests for TaskExecutor integration with PolicyEngine."""

from akari.execution.executor import TaskExecutor
from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.callable_runtime import CallableRuntime
from akari.execution.task import Task, TaskStatus
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import SpecKind, ToolSpec


def _make_registry_with_tool() -> IdentityRegistry:
    registry = IdentityRegistry()

    def multiply(a: int, b: int) -> int:
        return a * b

    tool = ToolSpec(
        id='tool:multiply',
        name='Multiply',
        runtime='callable',
        binding=multiply,
    )
    registry.register(tool)
    return registry


def _make_runtime_registry() -> RuntimeRegistry:
    rr = RuntimeRegistry()
    rr.register('callable', CallableRuntime())
    return rr


def test_task_executor_allows_when_policy_allows() -> None:
    """TaskExecutor should execute when policy explicitly allows."""
    registry = _make_registry_with_tool()
    runtime_registry = _make_runtime_registry()

    rules = [
        PolicyRule(
            id='allow-multiply',
            description='Allow calling multiply tool',
            subject_match='user:alice',
            action='tool.invoke',
            resource_match='tool:multiply',
            effect=PolicyEffect.ALLOW,
        )
    ]
    policy_set = PolicySet(name='test', rules=rules, version='v1')
    engine = PolicyEngine(policy_set)

    executor = TaskExecutor(
        registry=registry,
        runtime_registry=runtime_registry,
        policy_engine=engine,
    )

    task = Task(
        id='task:mul:1',
        subject='user:alice',
        target_id='tool:multiply',
        input={'a': 2, 'b': 3},
    )

    result = executor.run(task)

    assert task.status is TaskStatus.COMPLETED
    assert result.status is TaskStatus.COMPLETED
    assert result.output == 6


def test_task_executor_denies_when_policy_denies() -> None:
    """TaskExecutor should not call runtime when policy denies."""

    class FlagRuntime(CallableRuntime):
        def __init__(self) -> None:
            super().__init__()
            self.called = False

        def run(self, spec, task_input):
            self.called = True
            return super().run(spec, task_input)

    registry = IdentityRegistry()

    def multiply(a: int, b: int) -> int:
        return a * b

    tool = ToolSpec(
        id='tool:multiply',
        name='Multiply',
        runtime='callable',
        binding=multiply,
    )
    registry.register(tool)

    runtime_registry = RuntimeRegistry()
    flag_runtime = FlagRuntime()
    runtime_registry.register('callable', flag_runtime)

    rules = [
        PolicyRule(
            id='deny-multiply',
            description='Deny calling multiply tool',
            subject_match='*',
            action='tool.invoke',
            resource_match='tool:multiply',
            effect=PolicyEffect.DENY,
        )
    ]
    policy_set = PolicySet(name='test', rules=rules, version='v1')
    engine = PolicyEngine(policy_set)

    executor = TaskExecutor(
        registry=registry,
        runtime_registry=runtime_registry,
        policy_engine=engine,
    )

    task = Task(
        id='task:mul:2',
        subject='user:bob',
        target_id='tool:multiply',
        input={'a': 2, 'b': 3},
    )

    result = executor.run(task)

    assert task.status is TaskStatus.FAILED
    assert result.status is TaskStatus.FAILED
    assert result.output is None
    assert result.error is not None
    assert flag_runtime.called is False
