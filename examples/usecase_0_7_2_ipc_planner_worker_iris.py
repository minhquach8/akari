"""Use Case 0.7.2 – Planner/worker IPC for Iris prediction."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.execution.task import Task
from akari.ipc.agent_runtime import AgentRuntime
from akari.ipc.bus import InMemoryMessageBus
from akari.ipc.message import AgentMessage, MessageKind, MessageRole
from akari.registry.specs import ModelSpec


def prepare_kernel_with_iris() -> Kernel:
    kernel = Kernel()
    registry = kernel.get_registry()

    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(
        n_estimators=20,
        random_state=42,
    ).fit(X, y)

    spec = ModelSpec(
        id="model:iris_ipc_demo",
        name="Iris model for IPC demo",
        runtime="sklearn",
        binding=model,
    )
    registry.register(spec)
    return kernel


def main() -> None:
    kernel = prepare_kernel_with_iris()
    executor = kernel.get_executor()

    bus = InMemoryMessageBus()
    iris = load_iris()
    sample = iris.data[0:1]
    expected = iris.target[0]

    # Worker handler: run Task via executor.
    def worker_handler(msg: AgentMessage):
        if msg.kind is not MessageKind.TASK:
            return None

        target_id = msg.payload["target_id"]
        features = msg.payload["features"]

        task = Task(
            id="task:iris:demo",
            subject="agent:worker",
            target_id=target_id,
            input=features,
        )
        result = executor.run(task)

        return AgentMessage.new(
            sender="agent:worker",
            recipient=msg.sender,
            kind=MessageKind.TASK,
            role=MessageRole.WORKER,
            payload={"prediction": result.output},
            correlation_id=msg.correlation_id or msg.id,
        )

    # Planner handler: print prediction when received.
    def planner_handler(msg: AgentMessage):
        if msg.kind is MessageKind.TASK and "prediction" in msg.payload:
            prediction = msg.payload["prediction"][0]
            print(f"[agent:planner] received prediction: {prediction}")
            print(f"[agent:planner] expected class: {expected}")
        return None

    planner = AgentRuntime("agent:planner", bus, planner_handler)
    worker = AgentRuntime("agent:worker", bus, worker_handler)

    print("=== Use Case 0.7.2 – Planner/worker Iris ===\n")

    # Planner sends a task request.
    request = planner.send(
        to="agent:worker",
        kind=MessageKind.TASK,
        role=MessageRole.PLANNER,
        payload={
            "target_id": "model:iris_ipc_demo",
            "features": sample,
        },
    )
    print(f"[agent:planner] sent task request id={request.id}")

    # Worker processes the request and sends result.
    worker.run_once()
    # Planner processes response.
    planner.run_once()

    print("\nPlanner/worker round-trip completed.")


if __name__ == "__main__":
    main()
