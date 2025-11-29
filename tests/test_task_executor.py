"""Tests for TaskExecutor and runtime dispatch behaviour."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.execution.executor import TaskExecutor
from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.base import ModelRuntime
from akari.execution.task import Task, TaskStatus
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ModelSpec, ToolSpec


def test_task_executor_callable_runtime_success() -> None:
    """TaskExecutor should run a callable tool and complete successfully."""
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    # Register a simple multiply tool.
    def multiply(a: int, b: int) -> int:
        return a * b

    tool_spec = ToolSpec(
        id='tool:multiply',
        name='Multiply',
        runtime='callable',
        binding=multiply,
    )
    registry.register(tool_spec)

    # Create task targeting the tool.
    task = Task(
        id='task:multiply:1',
        subject='user:test',
        target_id='tool:multiply',
        input={'a': 2, 'b': 3},
    )

    executor = kernel.get_executor()
    result = executor.run(task)

    assert task.status is TaskStatus.COMPLETED
    assert result.status is TaskStatus.COMPLETED
    assert result.output == 6


def test_task_executor_sklearn_runtime_success() -> None:
    """TaskExecutor should run a sklearn model and match direct prediction."""
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)

    spec = ModelSpec(
        id='model:iris_exec_test',
        name='Iris exec test',
        runtime='sklearn',
        binding=model,
    )
    registry.register(spec)

    task = Task(
        id='task:iris:1',
        subject='agent:demo',
        target_id='model:iris_exec_test',
        input=X[:1],
    )

    executor = kernel.get_executor()
    result = executor.run(task)

    assert task.status is TaskStatus.COMPLETED
    assert result.status is TaskStatus.COMPLETED
    # Compare with direct model.predict
    direct = model.predict(X[:1])
    assert (result.output == direct).all()


def test_runtime_dispatch_uses_runtime_string_not_isinstance() -> None:
    """Runtime selection must be based on spec.runtime string."""

    class DummyRuntime(ModelRuntime):
        def __init__(self) -> None:
            self.called_with_id: str | None = None

        def run(self, spec, task_input):
            self.called_with_id = spec.id
            return 'dummy-output'

    registry = IdentityRegistry()
    runtime_registry = RuntimeRegistry()

    dummy_runtime = DummyRuntime()
    runtime_registry.register('dummy', dummy_runtime)

    # Note: binding is a callable, but runtime is "dummy" to ensure that
    # we do not dispatch based on isinstance(binding).
    spec = ToolSpec(
        id='tool:dummy',
        name='Dummy tool',
        runtime='dummy',
        binding=lambda x: x,  # should NOT matter for dispatch decision
    )
    registry.register(spec)

    executor = TaskExecutor(registry=registry, runtime_registry=runtime_registry)

    task = Task(
        id='task:dummy:1',
        subject=None,
        target_id='tool:dummy',
        input={'value': 1},
    )

    result = executor.run(task)

    assert task.status is TaskStatus.COMPLETED
    assert result.output == 'dummy-output'
    assert dummy_runtime.called_with_id == 'tool:dummy'
