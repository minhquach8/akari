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
from akari.registry.registry import IdentityRegistry
from akari.registry.specs import BaseSpec


class TaskExecutor:
    """Simple synchronous executor for Tasks."""
    
    def __init__(
        self,
        registry: IdentityRegistry,
        runtime_registry: RuntimeRegistry,
    ) -> None:
        self._registry = registry
        self._runtime_registry = runtime_registry
        
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
                    "target_id": task.target_id,
                    "runtime": None,
                }
            )
            
        # 3) Select runtime by spec.runtime (declarative)
        runtime_name = spec.runtime
        runtime = self._runtime_registry.get(runtime_name)
        
        # 4) Execute runtime
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
                    "target_id": task.target_id,
                    "runtime": runtime_name,
                }
            )
            
        # 5) Mark completed
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
                "target_id": task.target_id,
                "runtime": runtime_name,
            }
        )
        
    # ---- Internal helpers -----------------------------------------------
    
    def _resolve_spec(self, target_id: str) -> Optional[BaseSpec]:
        """Resolve a spec from the IdentityRegistry."""
        return self._registry.get(target_id)
