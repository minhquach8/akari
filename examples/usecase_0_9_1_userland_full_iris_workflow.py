"""Use Case 0.9.1 – Full Iris workflow via Workspace."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.userland.workspace import Workspace


def main() -> None:
    kernel = Kernel()
    workspace = Workspace("workspace:iris", kernel)

    iris = load_iris()
    X, y = iris.data, iris.target

    print("=== Use Case 0.9.1 – Full Iris workflow via Workspace ===\n")

    # 1. Register model.
    model = RandomForestClassifier(
        n_estimators=20,
        random_state=42,
    ).fit(X, y)

    workspace.register_model(
        model_id="model:iris_workspace",
        model=model,
        runtime="sklearn",
        name="Iris classifier (Workspace)",
        tags={"demo", "iris"},
    )
    print("Model registered as 'model:iris_workspace'.")

    # 2. Run prediction via Workspace.
    sample = X[0:1]
    expected = int(y[0])
    result = workspace.run_model(
        target_id="model:iris_workspace",
        input_data=sample,
        subject="user:demo",
    )
    print(f"\nPrediction via Workspace: {result.output[0]}")
    print(f"Expected label         : {expected}")

    # 3. Track experiment run + metrics + note.
    print("\nStarting experiment run...")
    with workspace.experiment_run(
        name="iris-workflow",
        parameters={"n_estimators": 20},
    ) as run_id:
        accuracy = float(model.score(X, y))
        workspace.log_metric(run_id, "accuracy", accuracy)
        workspace.log_note(
            channel="notes",
            content="Iris experiment with RandomForest (n_estimators=20).",
            metadata={"topic": "iris", "kind": "note"},
        )
        print(f"Logged accuracy={accuracy:.3f} to run {run_id}.")

    # 4. Query notes from memory.
    notes = workspace.search_memory(
        channel="notes",
        metadata_filters={"topic": "iris"},
    )
    print("\nNotes in memory (topic=iris):")
    for rec in notes:
        print(f"- {rec.content}")

    # 5. Show recent log events (nếu LogStore của bạn đang log task, policy...).
    events = workspace.get_logs(limit=5)
    print("\nLast log events (up to 5):")
    for ev in events:
        print(f"- {ev.timestamp} {ev.event_type}")

    print("\nWorkspace Iris workflow completed.")


if __name__ == "__main__":
    main()
