"""ToolManager for invoking tools via the registry and policy engine."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyDecision
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import SpecKind, ToolSpec

from .models import ToolInvocationResult
from .runtime import ToolRuntime


class ToolManager:
    """High-level manager for invoking tools registered in AKARI.

    Responsibilities:
        - Look up ToolSpec in the IdentityRegistry.
        - Check policy for:
            * "tool.invoke"
            * "resource.access" (if a resource_id is referenced).
        - Dispatch to the appropriate ToolRuntime based on spec.runtime.
    """

    def __init__(
        self,
        registry: IdentityRegistry,
        policy_engine: Optional[PolicyEngine] = None,
        runtime_registry: Optional[Mapping[str, ToolRuntime]] = None,
    ) -> None:
        self._registry = registry
        self._policy_engine = policy_engine
        self._runtime_registry: Dict[str, ToolRuntime] = dict(
            runtime_registry or {}
        )

    # ---- Runtime management --------------------------------------------

    def register_runtime(self, name: str, runtime: ToolRuntime) -> None:
        """Register or override a runtime under a given name."""
        self._runtime_registry[name] = runtime

    # ---- Invocation -----------------------------------------------------

    def invoke(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        subject: str,
        workspace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ToolInvocationResult:
        """Invoke a tool by id with the given arguments.

        The subject is the caller (user/agent) and is used for policy checks.
        """
        context = dict(context or {})

        spec = self._registry.get(tool_id)
        if spec is None:
            return ToolInvocationResult(
                success=False,
                error=f"Tool spec not found for id '{tool_id}'",
            )

        if spec.kind is not SpecKind.TOOL:
            return ToolInvocationResult(
                success=False,
                error=(
                    f"Spec '{tool_id}' is not a TOOL (kind={spec.kind.value})."
                ),
            )

        # Tool-level policy check.
        if self._policy_engine is not None:
            ctx = {
                "workspace": workspace,
                "runtime": spec.runtime,
                "tags": list(spec.tags),
            }
            ctx.update(context)
            decision: PolicyDecision = self._policy_engine.evaluate(
                subject=subject,
                action="tool.invoke",
                resource=spec.id,
                context=ctx,
            )
            if not decision.allowed:
                return ToolInvocationResult(
                    success=False,
                    error=f"Policy denied: {decision.reason}",
                )

        # Optional resource-level policy check if the tool references a resource.
        resource_id = arguments.get("resource_id")
        if resource_id and self._policy_engine is not None:
            ctx = {
                "workspace": workspace,
            }
            ctx.update(context)
            decision = self._policy_engine.evaluate(
                subject=subject,
                action="resource.access",
                resource=resource_id,
                context=ctx,
            )
            if not decision.allowed:
                return ToolInvocationResult(
                    success=False,
                    error=(
                        f"Policy denied for resource '{resource_id}': "
                        f"{decision.reason}"
                    ),
                )

        runtime = self._runtime_registry.get(spec.runtime)
        if runtime is None:
            return ToolInvocationResult(
                success=False,
                error=(
                    f"No ToolRuntime registered for runtime "
                    f"'{spec.runtime}'"
                ),
            )

        try:
            output = runtime.invoke(spec, arguments)
        except Exception as exc:  # pragma: no cover - defensive
            return ToolInvocationResult(success=False, error=str(exc))

        return ToolInvocationResult(success=True, output=output)
