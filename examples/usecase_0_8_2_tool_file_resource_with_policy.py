"""Use Case 0.8.2 – File resource with policy via ToolManager."""

from __future__ import annotations

from akari import Kernel
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.specs import ResourceSpec, ToolSpec


def build_kernel_with_resource_policy() -> Kernel:
    # Policy: allow tool.invoke for all, but only Alice may access the resource.
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
    policy_set = PolicySet(name="demo-tools-resources", rules=rules, version="v1")
    engine = PolicyEngine(policy_set)

    # Create Kernel with custom policy_engine.
    kernel = Kernel(policy_engine=engine)
    return kernel


def read_resource(resource_id: str) -> str:
    """Fake 'read' of a resource."""
    return f"fake read from {resource_id}"


def main() -> None:
    kernel = build_kernel_with_resource_policy()
    registry = kernel.get_registry()
    tool_manager = kernel.get_tool_manager()

    # Register file resource.
    resource = ResourceSpec(
        id="resource:demo_file",
        name="Demo file resource",
        runtime="file",
        metadata={"path": "/fake/path/demo.txt", "format": "text"},
        tags={"demo", "file"},
    )
    registry.register(resource)

    # Register read_resource tool.
    tool = ToolSpec(
        id="tool:read_resource",
        name="Read resource (fake)",
        runtime="callable",
        binding=read_resource,
        tags={"demo", "resource"},
    )
    registry.register(tool)

    print("=== Use Case 0.8.2 – File resource with policy ===\n")

    # Alice – allowed.
    alice_result = tool_manager.invoke(
        tool_id="tool:read_resource",
        arguments={"resource_id": "resource:demo_file"},
        subject="user:alice",
    )
    print("[user:alice] success:", alice_result.success)
    print("[user:alice] output:", alice_result.output)
    if alice_result.error:
        print("[user:alice] error:", alice_result.error)

    print()

    # Bob – denied.
    bob_result = tool_manager.invoke(
        tool_id="tool:read_resource",
        arguments={"resource_id": "resource:demo_file"},
        subject="user:bob",
    )
    print("[user:bob] success:", bob_result.success)
    print("[user:bob] output:", bob_result.output)
    if bob_result.error:
        print("[user:bob] error:", bob_result.error)


if __name__ == "__main__":
    main()
