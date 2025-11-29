"""Tests for ToolManager with callable tools."""

from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ToolSpec
from akari.tools.manager import ToolManager
from akari.tools.runtime import CallableToolRuntime


def _build_allow_all_tool_policy() -> PolicyEngine:
    rules = [
        PolicyRule(
            id="allow-all-tools",
            description="Allow all tool invocations",
            subject_match="*",
            action="tool.invoke",
            resource_match="*",
            effect=PolicyEffect.ALLOW,
        ),
    ]
    policy_set = PolicySet(name="tools", rules=rules, version="v1")
    return PolicyEngine(policy_set)


def test_callable_tool_invocation_via_tool_manager() -> None:
    registry = IdentityRegistry()
    policy_engine = _build_allow_all_tool_policy()
    manager = ToolManager(
        registry=registry,
        policy_engine=policy_engine,
        runtime_registry={"callable": CallableToolRuntime()},
    )

    def multiply(a: int, b: int) -> int:
        return a * b

    spec = ToolSpec(
        id="tool:multiply",
        name="Multiply two numbers",
        runtime="callable",
        binding=multiply,
    )
    registry.register(spec)

    result = manager.invoke(
        tool_id="tool:multiply",
        arguments={"a": 2, "b": 3},
        subject="user:test",
    )

    assert result.success is True
    assert result.output == 6
    assert result.error is None
