"""Tests for Task and TaskResult models in the execution subsystem."""

from datetime import datetime, timezone

from akari.execution.task import Task, TaskResult, TaskStatus


def test_task_default_status_and_timestamps() -> None:
    """Task should start in PENDING state with timestamps populated."""
    task = Task(
        id='task:1',
        subject='agent:demo',
        target_id='model:iris_sklearn',
        input={'x': [1, 2, 3]},
    )

    assert task.status is TaskStatus.PENDING
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)
    assert task.created_at.tzinfo is timezone.utc
    assert task.updated_at.tzinfo is timezone.utc


def test_task_status_transitions() -> None:
    """Task should support RUNNING, COMPLETED and FAILED transitions."""
    task = Task(
        id='task:2',
        subject='user:alice',
        target_id='tool:multiply',
        input={'a': 2, 'b': 3},
    )

    # Move to RUNNING
    task.mark_running()
    assert task.status is TaskStatus.RUNNING
    running_update_at = task.updated_at

    # Move to COMPLETED clears error.
    task.error = 'previous error'
    task.mark_completed()
    assert task.status is TaskStatus.COMPLETED
    assert task.error is None
    assert task.updated_at >= running_update_at

    # Move to FAILED set error and updates timestamp
    task.mark_failed('boom')
    assert task.status is TaskStatus.FAILED
    assert task.error == 'boom'
    assert task.updated_at >= running_update_at


def test_task_result_basic_fields() -> None:
    """TaskResult should hold output and error information."""
    now = datetime.now(timezone.utc)
    result = TaskResult(
        task_id='task:3',
        status=TaskStatus.COMPLETED,
        output={'y': 42},
        error=None,
        started_at=now,
        finished_at=now,
        metadata={'runtime': 'callable'},
    )

    assert result.task_id == 'task:3'
    assert result.status is TaskStatus.COMPLETED
    assert result.output == {'y': 42}
    assert result.error is None
    assert result.started_at == now
    assert result.finished_at == now
    assert result.metadata == {'runtime': 'callable'}
