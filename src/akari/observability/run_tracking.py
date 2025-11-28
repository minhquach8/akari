"""Experiment run tracking for AKARI."""

from __future__ import annotations

import json
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class MetricRecord:
    name: str
    value: float
    step: Optional[int] = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class ArtifactRecord:
    name: str
    data_or_path: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class ExperimentRun:
    """Single experiment run with metrics and artefacts."""

    id: str
    name: str
    params: Dict[str, Any]
    subject: Optional[str]
    workspace: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "running"
    metrics: List[MetricRecord] = field(default_factory=list)
    artifacts: List[ArtifactRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        def serialise(obj: Any) -> Any:
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, MetricRecord) or isinstance(obj, ArtifactRecord):
                data = asdict(obj)
                data["timestamp"] = obj.timestamp.isoformat()
                return data
            return obj

        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        if self.ended_at is not None:
            data["ended_at"] = self.ended_at.isoformat()
        data["metrics"] = [serialise(m) for m in self.metrics]
        data["artifacts"] = [serialise(a) for a in self.artifacts]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentRun":
        data = dict(data)
        data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("ended_at") is not None:
            data["ended_at"] = datetime.fromisoformat(data["ended_at"])

        metrics: List[MetricRecord] = []
        for m in data.get("metrics", []):
            metrics.append(
                MetricRecord(
                    name=m["name"],
                    value=m["value"],
                    step=m.get("step"),
                    timestamp=datetime.fromisoformat(m["timestamp"]),
                )
            )
        artifacts: List[ArtifactRecord] = []
        for a in data.get("artifacts", []):
            artifacts.append(
                ArtifactRecord(
                    name=a["name"],
                    data_or_path=a["data_or_path"],
                    timestamp=datetime.fromisoformat(a["timestamp"]),
                )
            )

        data["metrics"] = metrics
        data["artifacts"] = artifacts
        return cls(**data)


class RunStore(ABC):
    """Storage interface for experiment runs."""

    @abstractmethod
    def create(self, run: ExperimentRun) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, run: ExperimentRun) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, run_id: str) -> ExperimentRun:
        raise NotImplementedError

    @abstractmethod
    def list_runs(self) -> List[ExperimentRun]:
        raise NotImplementedError


class InMemoryRunStore(RunStore):
    """In-memory RunStore."""

    def __init__(self) -> None:
        self._runs: Dict[str, ExperimentRun] = {}

    def create(self, run: ExperimentRun) -> None:
        if run.id in self._runs:
            raise ValueError(f"Run {run.id} already exists")
        self._runs[run.id] = run

    def update(self, run: ExperimentRun) -> None:
        self._runs[run.id] = run

    def get(self, run_id: str) -> ExperimentRun:
        return self._runs[run_id]

    def list_runs(self) -> List[ExperimentRun]:
        return list(self._runs.values())


class JsonRunStore(RunStore):
    """Persistent RunStore using one JSON file per run."""

    def __init__(self, directory: str) -> None:
        self._directory = directory
        os.makedirs(directory, exist_ok=True)

    def _path_for(self, run_id: str) -> str:
        return os.path.join(self._directory, f"{run_id}.json")

    def create(self, run: ExperimentRun) -> None:
        path = self._path_for(run.id)
        if os.path.exists(path):
            raise ValueError(f"Run file already exists for id {run.id}")
        self._write(run)

    def update(self, run: ExperimentRun) -> None:
        self._write(run)

    def _write(self, run: ExperimentRun) -> None:
        path = self._path_for(run.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(run.to_dict(), f, indent=2)

    def get(self, run_id: str) -> ExperimentRun:
        path = self._path_for(run_id)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ExperimentRun.from_dict(data)

    def list_runs(self) -> List[ExperimentRun]:
        runs: List[ExperimentRun] = []
        for filename in os.listdir(self._directory):
            if not filename.endswith(".json"):
                continue
            run_id = filename[:-5]
            runs.append(self.get(run_id))
        return runs


class RunTracker:
    """High-level API for creating and updating experiment runs."""

    def __init__(self, store: RunStore) -> None:
        self._store = store

    def start_run(
        self,
        name: str,
        params: Dict[str, Any],
        subject: Optional[str] = None,
        workspace: Optional[str] = None,
    ) -> str:
        run_id = str(uuid.uuid4())
        run = ExperimentRun(
            id=run_id,
            name=name,
            params=params,
            subject=subject,
            workspace=workspace,
            started_at=datetime.now(timezone.utc),
        )
        self._store.create(run)
        return run_id

    def log_metric(
        self,
        run_id: str,
        name: str,
        value: float,
        step: Optional[int] = None,
    ) -> None:
        run = self._store.get(run_id)
        run.metrics.append(MetricRecord(name=name, value=value, step=step))
        self._store.update(run)

    def log_artifact(
        self,
        run_id: str,
        name: str,
        data_or_path: str,
    ) -> None:
        run = self._store.get(run_id)
        run.artifacts.append(
            ArtifactRecord(name=name, data_or_path=data_or_path)
        )
        self._store.update(run)

    def end_run(self, run_id: str, status: str = "completed") -> None:
        run = self._store.get(run_id)
        run.status = status
        run.ended_at = datetime.now(timezone.utc)
        self._store.update(run)
