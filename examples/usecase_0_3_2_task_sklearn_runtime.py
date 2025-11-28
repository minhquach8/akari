"""Use Case 0.3.2 – Task execution with SklearnRuntime."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.execution.task import Task
from akari.registry.specs import ModelSpec


def train_iris_model() -> RandomForestClassifier:
    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(n_estimators=20, random_state=42).fit(X, y)
    return model


def main() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None

    model = train_iris_model()
    spec = ModelSpec(
        id="model:iris_runtime",
        name="Iris classifier for runtime demo",
        runtime="sklearn",
        tags={"iris", "sklearn", "demo"},
        binding=model,
    )
    registry.register(spec)

    iris = load_iris()
    X = iris.data

    task = Task(
        id="task:iris:demo",
        subject="agent:demo",
        target_id="model:iris_runtime",
        input=X[:1],
    )

    executor = kernel.get_executor()
    result = executor.run(task)

    print("=== Use Case 0.3.2 – SklearnRuntime ===\n")
    print("Task status:", task.status.value)
    print("Result status:", result.status.value)
    print("Output prediction:", result.output)


if __name__ == "__main__":
    main()
