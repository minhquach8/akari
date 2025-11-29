"""Tests for autolog_experiment decorator."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.userland.experiments import autolog_experiment
from akari.userland.workspace import Workspace


@autolog_experiment(name="iris-autolog")
def train_and_evaluate(workspace: Workspace):
    """Dummy training function that returns metrics dict."""
    iris = load_iris()
    X, y = iris.data, iris.target

    model = RandomForestClassifier(
        n_estimators=5,
        random_state=42,
    ).fit(X, y)

    workspace.register_model(
        model_id="model:iris_autolog",
        model=model,
        runtime="sklearn",
    )

    accuracy = float(model.score(X, y))
    return {"accuracy": accuracy}


def test_autolog_experiment_creates_run_and_logs_metrics() -> None:
    kernel = Kernel()
    workspace = Workspace("workspace:iris", kernel)

    result = train_and_evaluate(workspace)
    assert isinstance(result, dict)
    assert "accuracy" in result

    runs = kernel.get_run_store().list_runs()
    assert len(runs) >= 1
