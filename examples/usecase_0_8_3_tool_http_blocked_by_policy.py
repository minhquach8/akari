"""Use Case 0.8.3 – HTTP tool blocked by policy."""

from __future__ import annotations

from akari import Kernel
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyCondition, PolicyEffect, PolicyRule, PolicySet
from akari.registry.specs import ToolSpec


def build_kernel_with_http_block_policy() -> Kernel:
    def is_untrusted_http(context: dict) -> bool:
        return (
            context.get("runtime") == "http"
            and context.get("domain") == "untrusted.example.com"
        )

    cond = PolicyCondition(
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
            conditions=[cond],
        ),
    ]
    policy_set = PolicySet(name="http-tools", rules=rules, version="v1")
    engine = PolicyEngine(policy_set)
    kernel = Kernel(policy_engine=engine)
    return kernel


def main() -> None:
    kernel = build_kernel_with_http_block_policy()
    registry = kernel.get_registry()
    tool_manager = kernel.get_tool_manager()

    # HTTP tool pointing at an untrusted domain.
    http_tool = ToolSpec(
        id="tool:http_untrusted",
        name="HTTP GET untrusted",
        runtime="http",
        binding=None,
        metadata={
            "url": "https://untrusted.example.com/api",
            "domain": "untrusted.example.com",
            "method": "GET",
        },
        tags={"demo", "http"},
    )
    registry.register(http_tool)

    print("=== Use Case 0.8.3 – HTTP tool blocked by policy ===\n")

    result = tool_manager.invoke(
        tool_id="tool:http_untrusted",
        arguments={"path": "/demo"},
        subject="user:alice",
        context={"domain": "untrusted.example.com"},
    )

    print("Invocation success:", result.success)
    print("Output:", result.output)
    print("Error:", result.error)


if __name__ == "__main__":
    main()
