"""Use Case 0.6.1 – Experiment runs for Iris training."""

from __future__ import annotations

from typing import Dict

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from akari.observability.run_tracking import InMemoryRunStore, RunTracker


def train_iris_model(n_estimators: int) -> float:
    iris = load_iris()
    X, y = iris.data, iris.target

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=42,
    ).fit(X, y)

    y_pred = model.predict(X)
    return float(accuracy_score(y, y_pred))


def main() -> None:
    store = InMemoryRunStore()
    tracker = RunTracker(store)

    configs = [
        {"n_estimators": 10},
        {"n_estimators": 50},
    ]

    for cfg in configs:
        n_estimators = cfg["n_estimators"]
        run_id = tracker.start_run(
            name="iris_random_forest",
            params=cfg,
            subject="user:experimenter",
            workspace="demo",
        )
        acc = train_iris_model(n_estimators)
        tracker.log_metric(run_id, "accuracy", acc, step=1)
        tracker.end_run(run_id, status="completed")

    print("=== Use Case 0.6.1 – Iris experiment runs ===\n")
    for run in store.list_runs():
        params: Dict[str, int] = run.params
        accs = [m for m in run.metrics if m.name == "accuracy"]
        acc_val = accs[-1].value if accs else None
        print(
            f"Run {run.id}: n_estimators={params['n_estimators']}, "
            f"accuracy={acc_val}"
        )


if __name__ == "__main__":
    main()
