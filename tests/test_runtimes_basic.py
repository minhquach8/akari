"""Tests for CallableRuntime, SklearnRuntime and RuntimeRegistry."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.callable_runtime import CallableRuntime
from akari.execution.runtimes.sklearn_runtime import SklearnRuntime
from akari.registry.specs import ModelSpec, ToolSpec


def test_callable_runtime_basic():
    def mul(a, b):
        return a * b

    spec = ToolSpec(
        id='tool:mul',
        name='Multiply',
        runtime='callable',
        binding=mul,
    )

    rt = CallableRuntime()
    out = rt.run(spec, {'a': 2, 'b': 3})
    assert out == 6


def test_sklearn_runtime_basic():
    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(n_estimators=5).fit(X, y)

    spec = ModelSpec(
        id='model:test_sklearn',
        name='Test',
        runtime='sklearn',
        binding=model,
    )

    rt = SklearnRuntime()
    pred = rt.run(spec, X[:1])
    assert pred.shape == (1,)


def test_runtime_registry():
    reg = RuntimeRegistry()

    reg.register('callable', CallableRuntime())
    reg.register('sklearn', SklearnRuntime())

    assert 'callable' in reg.list_runtimes()
    assert 'sklearn' in reg.list_runtimes()

    rt = reg.get('callable')
    assert isinstance(rt, CallableRuntime)
