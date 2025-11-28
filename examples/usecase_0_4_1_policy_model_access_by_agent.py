"""Use Case 0.4.1 – Policy: allow/deny model access by agent."""

from __future__ import annotations

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

from akari.execution.executor import TaskExecutor
from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.sklearn_runtime import SklearnRuntime
from akari.execution.task import Task, TaskStatus
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ModelSpec


def build_iris_spec(registry: IdentityRegistry) -> None:
    iris = load_iris()
    X, y = iris.data, iris.target
    model = RandomForestClassifier(n_estimators=20, random_state=42).fit(X, y)

    spec = ModelSpec(
        id="model:iris_policy",
        name="Iris model for policy demo",
        runtime="sklearn",
        binding=model,
    )
    registry.register(spec)


def build_policy_engine() -> PolicyEngine:
    rules = [
        PolicyRule(
            id="allow-planner-iris",
            description="Planner agent may invoke iris models",
            subject_match="agent:planner",
            action="model.invoke",
            resource_match="model:iris*",
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id="deny-others-iris",
            description="Deny others by default (implicit via fail-closed)",
            subject_match="agent:blocked",
            action="model.invoke",
            resource_match="model:iris*",
            effect=PolicyEffect.DENY,
        ),
    ]
    policy_set = PolicySet(name="demo", rules=rules, version="v1")
    return PolicyEngine(policy_set)


def main() -> None:
    registry = IdentityRegistry()
    build_iris_spec(registry)

    runtime_registry = RuntimeRegistry()
    runtime_registry.register("sklearn", SklearnRuntime())

    policy_engine = build_policy_engine()
    executor = TaskExecutor(
        registry=registry,
        runtime_registry=runtime_registry,
        policy_engine=policy_engine,
    )

    iris = load_iris()
    X = iris.data[:1]

    # Allowed agent
    allowed_task = Task(
        id="task:iris:allowed",
        subject="agent:planner",
        target_id="model:iris_policy",
        input=X,
    )
    allowed_result = executor.run(allowed_task)

    # Denied agent
    denied_task = Task(
        id="task:iris:denied",
        subject="agent:blocked",
        target_id="model:iris_policy",
        input=X,
    )
    denied_result = executor.run(denied_task)

    print("=== Use Case 0.4.1 – Policy model access by agent ===\n")
    print("Allowed task status:", allowed_task.status.value)
    print("Allowed result status:", allowed_result.status.value)
    print("Denied task status:", denied_task.status.value)
    print("Denied result status:", denied_result.status.value)
    print("Denied error:", denied_result.error)


if __name__ == "__main__":
    main()
