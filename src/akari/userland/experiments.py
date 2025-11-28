"""Experiment helpers built on top of Workspace and RunTracker."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from akari.observability.run_tracking import RunTracker

if False:  # pragma: no cover
    from akari.userland.workspace import Workspace  # type: ignore[unused-import]


@dataclass
class SimpleExperiment:
    """Small wrapper around a single experiment run."""

    workspace: "Workspace"
    name: str
    params: Dict[str, Any]
    run_id: str

    @classmethod
    def start(
        cls,
        workspace: "Workspace",
        name: str,
        params: Dict[str, Any],
        subject: str = "user:workspace",
    ) -> "SimpleExperiment":
        tracker = RunTracker(workspace.kernel.get_run_store())
        run_id = tracker.start_run(
            name=name,
            params=params,
            subject=subject,
            workspace=workspace.workspace_id,
        )
        return cls(workspace=workspace, name=name, params=params, run_id=run_id)

    def log_metric(self, name: str, value: float, step: int = 0) -> None:
        tracker = RunTracker(self.workspace.kernel.get_run_store())
        tracker.log_metric(self.run_id, name, value, step)

    def log_artifact(self, name: str, data_or_path: Any) -> None:
        tracker = RunTracker(self.workspace.kernel.get_run_store())
        tracker.log_artifact(self.run_id, name, data_or_path)


class TrackedExperimentRunner:
    """Helper to run a function inside an experiment_run and autolog metrics."""

    def __init__(self, workspace: "Workspace") -> None:
        self.workspace = workspace

    def run(
        self,
        name: str,
        params: Dict[str, Any],
        fn: Callable[..., Dict[str, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Run fn(*args, **kwargs) under an experiment_run.

        If fn returns a dict, its key/value pairs are logged as metrics.
        """
        with self.workspace.experiment_run(name, params) as run_id:
            metrics = fn(*args, **kwargs)
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    self.workspace.log_metric(run_id, key, float(value), step=0)
            return run_id


def autolog_experiment(
    name: str,
    params_fn: Optional[Callable[..., Dict[str, Any]]] = None,
):
    """Decorator to wrap a training/eval function with experiment logging.

    The decorated function must accept a Workspace as its first argument
    and may return a dict of metrics which will be logged.
    """

    def decorator(fn: Callable[..., Any]):
        def wrapper(workspace: "Workspace", *args: Any, **kwargs: Any):
            params: Dict[str, Any] = (
                params_fn(*args, **kwargs) if params_fn is not None else {}
            )
            with workspace.experiment_run(name, params) as run_id:
                result = fn(workspace, *args, **kwargs)
                if isinstance(result, dict):
                    for key, value in result.items():
                        workspace.log_metric(run_id, key, float(value), step=0)
                return result

        return wrapper

    return decorator
