"""Tests for Workspace Iris workflow."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.userland.workspace import Workspace


def test_workspace_register_and_run_model() -> None:
    kernel = Kernel()
    workspace = Workspace("workspace:iris", kernel)

    iris = load_iris()
    X, y = iris.data, iris.target

    model = RandomForestClassifier(
        n_estimators=10,
        random_state=42,
    ).fit(X, y)

    workspace.register_model(
        model_id="model:iris_workspace",
        model=model,
        runtime="sklearn",
        name="Iris via Workspace",
        tags={"demo", "iris"},
    )

    sample = X[0:1]
    expected = int(y[0])

    result = workspace.run_model(
        target_id="model:iris_workspace",
        input_data=sample,
        subject="user:test",
    )

    assert result.status == "completed"
    assert int(result.output[0]) == expected


def test_workspace_experiment_run_logs_metrics() -> None:
    kernel = Kernel()
    workspace = Workspace("workspace:iris", kernel)

    with workspace.experiment_run(
        name="iris-experiment",
        parameters={"n_estimators": 10},
    ) as run_id:
        workspace.log_metric(run_id, "accuracy", 1.0)

    runs = kernel.get_run_store().list_runs()
    # Có run với param n_estimators=10.
    assert any(r.params.get("n_estimators") == 10 for r in runs)
