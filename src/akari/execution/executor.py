"""
Synchronous TaskExecutor for AKARI.

The TaskExecutor coordinates:
- resolving specs from the IdentityRegistry,
- selecting a runtime via RuntimeRegistry,
- executing the spec.binding with the task input,
- updating Task status and producing a TaskResult.

At v0.3.0 there is no policy or observability integration yet.
Those will be hooked in later via additional layers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.task import Task, TaskResult, TaskStatus
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyDecision
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import BaseSpec, SpecKind


class TaskExecutor:
    """Simple synchronous executor for Tasks."""

    def __init__(
        self,
        registry: IdentityRegistry,
        runtime_registry: RuntimeRegistry,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self._registry = registry
        self._runtime_registry = runtime_registry
        self._policy_engine = policy_engine

    # ---- Policy hook ----------------------------------------------------

    def authorise(
        self,
        subject: str | None,
        action: str,
        resource: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyDecision | None:
        """Authorise a request via PolicyEngine if configured.

        If no policy_engine is attached, this returns None and the caller should treat the request as allowed (for backwards compatibility).

        At v0.4.0 the core semantics are:
        - If policy_engine is present, its decision is authoritative.
        - If no policy_engine, execution proceeds without checks.
        """
        if self._policy_engine is None:
            return None

        ctx = context or {}
        # Normalise subject so PolicyEngine always sees a string.
        subject_id = subject or 'unknown'
        return self._policy_engine.evaluate(
            subject=subject_id,
            action=action,
            resource=resource,
            context=ctx,
        )

    # ---- Core API -------------------------------------------------------

    def run(self, task: Task) -> TaskResult:
        """
        Execute a Task and return a TaskResult.

        Behaviour:
        - Resolve spec from registry via task.target_id.
        - Look up runtime via spec.runtime string.
        - Call runtime.run(spec, task.input).
        - Update task.status and timestamps.
        - Wrap the outcome in a TaskResult.
        """
        started_at = datetime.now(timezone.utc)

        # 1) Mark running.
        task.mark_running()

        # 2) Resolve spec.
        spec = self._resolve_spec(task.target_id)
        if spec is None:
            error_msg = f"Spec not found for target_id='{task.target_id}'"
            task.mark_failed(error_msg)
            finished_at = datetime.now(timezone.utc)
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                output=None,
                error=error_msg,
                started_at=started_at,
                finished_at=finished_at,
                metadata={
                    'target_id': task.target_id,
                    'runtime': None,
                },
            )

        # 3) Policy check (if configured).
        action = self._derive_action_from_spec(spec)
        resource_id = spec.id
        context = {
            'workspace': task.workspace,
            'runtime': spec.runtime,
            'spec_kind': spec.kind.value,
            'task_metadata': task.metadata,
        }

        decision = self.authorise(
            subject=task.subject,
            action=action,
            resource=resource_id,
            context=context,
        )

        if decision is not None and not decision.allowed:
            error_msg = f'Policy denied: {decision.reason}'
            task.mark_failed(error_msg)
            finished_at = datetime.now(timezone.utc)
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                output=None,
                error=error_msg,
                started_at=started_at,
                finished_at=finished_at,
                metadata={
                    'target_id': spec.id,
                    'runtime': spec.runtime,
                    'policy_rule_id': decision.rule_id,
                    'policy_reason': decision.reason,
                },
            )

        # 4) Select runtime by spec.runtime (declarative).
        runtime_name = spec.runtime
        runtime = self._runtime_registry.get(runtime_name)

        # 5) Execute runtime.
        try:
            output = runtime.run(spec, task.input)
        except Exception as exc:
            error_msg = str(exc)
            task.mark_failed(error_msg)
            finished_at = datetime.now(timezone.utc)
            return TaskResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                output=None,
                error=error_msg,
                started_at=started_at,
                finished_at=finished_at,
                metadata={
                    'target_id': task.target_id,
                    'runtime': runtime_name,
                },
            )

        # 6) Mark completed
        task.mark_completed()
        finished_at = datetime.now(timezone.utc)

        return TaskResult(
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            output=output,
            error=None,
            started_at=started_at,
            finished_at=finished_at,
            metadata={
                'target_id': task.target_id,
                'runtime': runtime_name,
            },
        )

    # ---- Internal helpers -----------------------------------------------

    def _derive_action_from_spec(self, spec: BaseSpec) -> str:
        """
        Derive the policy action string from the spec kind.

        At v0.4.0 we use a simple mapping:

        - model  -> "model.invoke"
        - agent  -> "agent.invoke"
        - tool   -> "tool.invoke"
        - resource -> "resource.access"
        - workspace -> "workspace.access"
        """
        if spec.kind is SpecKind.MODEL:
            return 'model.invoke'
        if spec.kind is SpecKind.AGENT:
            return 'agent.invoke'
        if spec.kind is SpecKind.TOOL:
            return 'tool.invoke'
        if spec.kind is SpecKind.RESOURCE:
            return 'resource.access'
        if spec.kind is SpecKind.WORKSPACE:
            return 'workspace.access'
        # Fallback for unknown kinds.
        return 'resource.access'

    def _resolve_spec(self, target_id: str) -> Optional[BaseSpec]:
        """Resolve a spec from the IdentityRegistry."""
        return self._registry.get(target_id)
