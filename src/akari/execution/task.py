"""
Core task models for the AKARI execution subsystem.

This module defines the Task and TaskResult types that represent the standardised "unit of work" in AKARI.

At v0.3.1 there is no actual execution engine yet. These models are focused on:
- capturing the intent of a run (Task),
- and the outcome of a run (TaskResult),
in a way that will be compatible with later policy, observability and runtime components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class TaskStatus(str, Enum):
    """Lifecycle states for a Task."""

    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


@dataclass
class Task:
    """
    Standard representation of a unit of work in AKARI.

    Fields:
        id:
            Unique identifier for this task.
        subject:
            Identifier of the initiating subject (user id, agent id, etc.).
        workspace:
            Optional workspace / project context for the task.
        target_id:
            Registry id of the target spec to invoke, e.g. "model:iris".
        input:
            Arbitrary input payload for the runtime (features, params, etc.).
        status:
            Current lifecycle status (pending, running, completed, failed).
        created_at:
            Timestamp when the task object was created.
        updated_at:
            Timestamp of the last status or field update.
        error:
            Optional error message if the task failed.
        risk_level:
            Reserved field for future risk classification (e.g. "low", "medium", "high").
        metadata:
            Free-form metadata for tracking and observability.
        explanation:
            Reserved field for future explanation / XAI data.
    """

    id: str
    subject: Optional[str]
    target_id: str
    input: Any

    workspace: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    error: Optional[str] = None
    risk_level: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    explanation: Optional[Any] = None

    def mark_running(self) -> None:
        """Mark the task as running and update the timestamp"""
        self.status = TaskStatus.RUNNING
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """Mark the task as completed and update the timestamp"""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)
        self.error = None  # Clear error on completion

    def mark_failed(self, error: str) -> None:
        """Mark the task as failed with an error message"""
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)
        self.error = error


@dataclass
class TaskResult:
    """
    Outcome of executing a Task.

    Fields:
        task_id:
            Identifier of the originating task.
        status:
            Final status of the task (completed or failed).
        output:
            Result payload from the runtime, if any.
        error:
            Error message if the task failed, else None.
        started_at:
            Timestamp when execution started.
        finished_at:
            Timestamp when execution finished.
        metadata:
            Additional metadata about the run (runtime details, metrics, etc.).
    """

    task_id: str
    status: TaskStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
