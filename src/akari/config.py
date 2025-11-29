"""Configuration model and loader for booting the AKARI Kernel."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import yaml  # type: ignore[import]  # requires pyyaml


@dataclass
class ObservabilityConfig:
    """Configuration for logging and run tracking backends."""

    log_backend: str = "memory"  # "memory" | "jsonl"
    log_path: Optional[str] = None

    run_backend: str = "memory"  # "memory" | "json"
    run_dir: Optional[str] = None


@dataclass
class ExecutionConfig:
    """Configuration for execution/runtime behaviour.

    For v1.0.0 only a small subset is used. The rest is reserved for
    future features (HF / PyTorch device, additional runtimes).
    """

    enable_runtimes: Optional[List[str]] = None
    hf_device: Optional[str] = None
    hf_dtype: Optional[str] = None


@dataclass
class AkariConfig:
    """Top-level configuration for booting the AKARI Kernel."""

    observability: ObservabilityConfig = field(
        default_factory=ObservabilityConfig
    )
    execution: ExecutionConfig = field(
        default_factory=ExecutionConfig
    )
    policy_files: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AkariConfig":
        """Construct an AkariConfig from a plain dictionary."""
        obs_data = data.get("observability", {}) or {}
        exe_data = data.get("execution", {}) or {}

        observability = ObservabilityConfig(
            log_backend=obs_data.get("log_backend", "memory"),
            log_path=obs_data.get("log_path"),
            run_backend=obs_data.get("run_backend", "memory"),
            run_dir=obs_data.get("run_dir"),
        )

        execution = ExecutionConfig(
            enable_runtimes=exe_data.get("enable_runtimes"),
            hf_device=exe_data.get("hf_device"),
            hf_dtype=exe_data.get("hf_dtype"),
        )

        policy_files = data.get("policy_files")

        return cls(
            observability=observability,
            execution=execution,
            policy_files=policy_files,
        )

    @classmethod
    def from_yaml(cls, path: str) -> "AkariConfig":
        """Load configuration from a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        if not isinstance(raw, dict):
            raise ValueError(f"Config file {path} must contain a mapping at the top level.")
        return cls.from_dict(raw)

    @classmethod
    def load(cls, source: Union[str, Dict[str, Any]]) -> "AkariConfig":
        """Convenience loader from either path or dictionary."""
        if isinstance(source, str):
            return cls.from_yaml(source)
        if isinstance(source, dict):
            return cls.from_dict(source)
        raise TypeError("AkariConfig.load() expects a file path or a dict.")
