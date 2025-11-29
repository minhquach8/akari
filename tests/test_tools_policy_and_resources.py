"""Tests for ToolManager policy behaviour with resources and HTTP tools."""

from akari.policy.engine import PolicyEngine
from akari.policy.models import (
    PolicyCondition,
    PolicyDecision,
    PolicyEffect,
    PolicyRule,
    PolicySet,
)
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import ResourceSpec, ToolSpec
from akari.tools.manager import ToolManager
from akari.tools.runtime import CallableToolRuntime, HttpToolRuntime


def _build_resource_policy_engine() -> PolicyEngine:
    """Allow tool.invoke for all tools, but restrict resource.access."""
    rules = [
        PolicyRule(
            id="allow-all-tools",
            description="Allow all tool invocations",
            subject_match="*",
            action="tool.invoke",
            resource_match="*",
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id="allow-demo-file-for-alice",
            description="Allow Alice to access demo file resource",
            subject_match="user:alice",
            action="resource.access",
            resource_match="resource:demo_file",
            effect=PolicyEffect.ALLOW,
        ),
    ]
    policy_set = PolicySet(name="tools-resources", rules=rules, version="v1")
    return PolicyEngine(policy_set)


def _build_http_block_policy_engine() -> PolicyEngine:
    """Deny HTTP tools targeting untrusted domains."""

    def is_untrusted_http(context: dict) -> bool:
        return (
            context.get("runtime") == "http"
            and context.get("domain") == "untrusted.example.com"
        )

    deny_untrusted_condition = PolicyCondition(
        name="is-untrusted-http",
        predicate=is_untrusted_http,
    )

    rules = [
        PolicyRule(
            id="deny-untrusted-http",
            description="Deny HTTP tools for untrusted.example.com",
            subject_match="*",
            action="tool.invoke",
            resource_match="tool:http_*",
            effect=PolicyEffect.DENY,
            conditions=[deny_untrusted_condition],
        ),
    ]
    policy_set = PolicySet(name="http-tools", rules=rules, version="v1")
    return PolicyEngine(policy_set)


def test_resource_access_policy_enforced() -> None:
    registry = IdentityRegistry()
    policy_engine = _build_resource_policy_engine()
    manager = ToolManager(
        registry=registry,
        policy_engine=policy_engine,
        runtime_registry={"callable": CallableToolRuntime()},
    )

    # Resource spec.
    resource = ResourceSpec(
        id="resource:demo_file",
        name="Demo file resource",
        runtime="file",
        metadata={"path": "/fake/path/demo.txt"},
    )
    registry.register(resource)

    # Tool that (fake) reads a resource by id.
    def read_resource(resource_id: str) -> str:
        return f"fake read from {resource_id}"

    tool = ToolSpec(
        id="tool:read_resource",
        name="Read resource",
        runtime="callable",
        binding=read_resource,
    )
    registry.register(tool)

    # Alice is allowed to access the resource.
    allowed_result = manager.invoke(
        tool_id="tool:read_resource",
        arguments={"resource_id": "resource:demo_file"},
        subject="user:alice",
    )
    assert allowed_result.success is True
    assert "resource:demo_file" in str(allowed_result.output)

    # Bob is denied by fail-closed (no matching resource.access rule).
    denied_result = manager.invoke(
        tool_id="tool:read_resource",
        arguments={"resource_id": "resource:demo_file"},
        subject="user:bob",
    )
    assert denied_result.success is False
    assert "Policy denied" in (denied_result.error or "")


def test_http_tool_blocked_for_untrusted_domain() -> None:
    registry = IdentityRegistry()
    policy_engine = _build_http_block_policy_engine()
    manager = ToolManager(
        registry=registry,
        policy_engine=policy_engine,
        runtime_registry={"http": HttpToolRuntime()},
    )

    http_spec = ToolSpec(
        id="tool:http_untrusted",
        name="HTTP GET untrusted",
        runtime="http",
        binding=None,
        metadata={
            "url": "https://untrusted.example.com/api",
            "domain": "untrusted.example.com",
            "method": "GET",
        },
    )
    registry.register(http_spec)

    result = manager.invoke(
        tool_id="tool:http_untrusted",
        arguments={"path": "/demo"},
        subject="user:alice",
        context={"domain": "untrusted.example.com"},
    )

    assert result.success is False
    assert "Policy denied" in (result.error or "")
