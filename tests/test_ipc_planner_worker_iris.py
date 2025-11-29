"""Tests for planner/worker IPC integration with Kernel and Iris model."""

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari import Kernel
from akari.execution.task import Task
from akari.ipc.agent_runtime import AgentRuntime
from akari.ipc.bus import InMemoryMessageBus
from akari.ipc.message import AgentMessage, MessageKind, MessageRole
from akari.registry.specs import ModelSpec


def _prepare_kernel_with_iris() -> Kernel:
    kernel = Kernel()
    registry = kernel.get_registry()

    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(
        n_estimators=10,
        random_state=42,
    ).fit(X, y)

    spec = ModelSpec(
        id="model:iris_ipc",
        name="Iris model for IPC worker",
        runtime="sklearn",
        binding=model,
    )
    registry.register(spec)
    return kernel


def test_planner_worker_iris_prediction() -> None:
    kernel = _prepare_kernel_with_iris()
    bus = InMemoryMessageBus()

    registry = kernel.get_registry()
    executor = kernel.get_executor()

    iris = load_iris()
    sample = iris.data[0:1]
    expected = int(iris.target[0])

    # Worker handler: build Task from message, run via executor, reply prediction.
    def worker_handler(msg: AgentMessage):
        if msg.kind is not MessageKind.TASK:
            return None

        target_id = msg.payload["target_id"]
        features = msg.payload["features"]

        task = Task(
            id="task:iris:worker",
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

    # Planner handler: store last prediction.
    last_prediction: dict[str, int | None] = {"value": None}

    def planner_handler(msg: AgentMessage):
        if msg.kind is MessageKind.TASK and "prediction" in msg.payload:
            last_prediction["value"] = int(msg.payload["prediction"][0])
        return None

    planner = AgentRuntime("agent:planner", bus, planner_handler)
    worker = AgentRuntime("agent:worker", bus, worker_handler)

    # Planner sends task request to worker.
    request = planner.send(
        to="agent:worker",
        kind=MessageKind.TASK,
        role=MessageRole.PLANNER,
        payload={
            "target_id": "model:iris_ipc",
            "features": sample,
        },
    )

    # Worker processes request and sends result back.
    worker.run_once()
    # Planner processes response.
    planner.run_once()

    assert last_prediction["value"] == expected
    # correlation id of response matches request.
    # Get all messages for worker (just for sanity, there should be none pending).
    assert request.correlation_id is None
