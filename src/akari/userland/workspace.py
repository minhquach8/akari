"""User-facing Workspace façade for AKARI."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from akari.core.kernel import Kernel
from akari.execution.task import Task, TaskResult
from akari.observability.run_tracking import RunTracker
from akari.registry.specs import ModelSpec
from akari.tools.manager import ToolManager


@dataclass
class Workspace:
    """High-level façade over the Kernel for a specific workspace.

    This gives a simpler API for:
        - model registration and invocation,
        - experiment runs and metrics,
        - symbolic/vector memory,
        - accessing logs,
        - invoking tools.
    """

    workspace_id: str
    kernel: Kernel

    def __post_init__(self) -> None:
        self._registry = self.kernel.get_registry()
        self._executor = self.kernel.get_executor()
        self._memory = self.kernel.get_memory()
        self._logger = self.kernel.get_logger()
        self._run_tracker = RunTracker(self.kernel.get_run_store())
        self._tools: ToolManager = self.kernel.get_tool_manager()

    # ------------------------------------------------------------------
    # Model registration & invocation
    # ------------------------------------------------------------------

    def register_model(
        self,
        model_id: str,
        model: Any,
        runtime: str,
        name: Optional[str] = None,
        tags: Optional[Iterable[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelSpec:
        """Register a model in the registry within this workspace context."""
        spec = ModelSpec(
            id=model_id,
            name=name or model_id,
            runtime=runtime,
            binding=model,
            tags=set(tags or []),
            metadata=metadata or {},
        )
        self._registry.register(spec)
        return spec

    def run_model(
        self,
        target_id: str,
        input_data: Any,
        subject: str = 'user:workspace',
    ) -> TaskResult:
        """Run a registered model via the TaskExecutor."""
        task = Task(
            id=f'task:{target_id}:{subject}',
            subject=subject,
            workspace=self.workspace_id,
            target_id=target_id,
            input=input_data,
        )
        return self._executor.run(task)

    # ------------------------------------------------------------------
    # Experiments & metrics
    # ------------------------------------------------------------------

    @contextmanager
    def experiment_run(
        self,
        name: str,
        parameters: Dict[str, Any],
        subject: str = 'user:workspace',
    ):
        """Context manager for tracking an experiment run on this workspace."""
        run_id = self._run_tracker.start_run(
            name=name,
            params=parameters,
            subject=subject,
            workspace=self.workspace_id,
        )
        try:
            yield run_id
            # Mark success with status metric = 1.0.
            self._run_tracker.log_metric(
                run_id=run_id,
                name='status',
                value=1.0,
                step=0,
            )
        except Exception:
            # Mark failure with status metric = 0.0.
            self._run_tracker.log_metric(
                run_id=run_id,
                name='status',
                value=0.0,
                step=0,
            )
            raise

    def log_metric(
        self,
        run_id: str,
        name: str,
        value: float,
        step: int = 0,
    ) -> None:
        """Log a scalar metric for a given experiment run."""
        self._run_tracker.log_metric(run_id=run_id, name=name, value=value, step=step)

    def log_artifact(
        self,
        run_id: str,
        name: str,
        data_or_path: Any,
    ) -> None:
        """Log an artefact for a given experiment run."""
        self._run_tracker.log_artifact(
            run_id=run_id, name=name, data_or_path=data_or_path
        )

    # ------------------------------------------------------------------
    # Memory helpers
    # ------------------------------------------------------------------

    def log_note(
        self,
        channel: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        subject: str = 'user:workspace',
        classification: str = 'internal',
    ) -> None:
        """Write a symbolic note into memory.

        This generates a simple record_id automatically.
        """
        record_id = f'{channel}:{uuid.uuid4().hex}'
        self._memory.write_symbolic(
            channel=channel,
            record_id=record_id,
            content=content,
            subject=subject,
            metadata=metadata or {},
            classification=classification,
        )

    def search_memory(
        self,
        channel: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
        text_contains: Optional[str] = None,
        subject: str = 'user:workspace',
    ) -> List[Any]:
        """Query symbolic memory by metadata and/or text content."""
        return self._memory.query_symbolic(
            channel=channel,
            subject=subject,
            metadata_filters=metadata_filters or {},
            text_contains=text_contains,
        )

    def index_document(
        self,
        channel: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        subject: str = 'user:workspace',
    ) -> None:
        """Index a document into the vector store for semantic search.

        A simple record_id is generated automatically.
        """
        record_id = f'{channel}:{uuid.uuid4().hex}'
        self._memory.index_vector(
            channel=channel,
            record_id=record_id,
            text=text,
            subject=subject,
            metadata=metadata or {},
        )

    def search_documents(
        self,
        channel: str,
        query_text: str,
        top_k: int = 3,
        subject: str = 'user:workspace',
    ) -> List[Any]:
        """Search documents semantically in the vector store."""
        return self._memory.search_vector(
            channel=channel,
            query_text=query_text,
            subject=subject,
            top_k=top_k,
        )

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    def get_logs(
        self,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Any]:
        """Fetch recent log events, optionally filtered by type and limited."""
        events = self._logger.list_events()
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if limit is not None:
            events = events[-limit:]
        return events

    # ------------------------------------------------------------------
    # Tools
    # ------------------------------------------------------------------

    def call_tool(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        subject: str = 'user:workspace',
    ):
        """Invoke a tool via the ToolManager."""
        return self._tools.invoke(
            tool_id=tool_id,
            arguments=arguments,
            subject=subject,
            workspace=self.workspace_id,
        )
