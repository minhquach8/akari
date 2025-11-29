from __future__ import annotations

from enum import Enum


class SubsystemName (str, Enum):
    """
    Canonical names for AKARI subsystems.
    
    This keeps a single source of truth for how subsystems are identified across logging, configuration, and user-facing APIs.
    """
    
    REGISTRY = "registry"
    EXECUTOR = "executor"
    POLICY_ENGINE = "policy_engine"
    MEMORY = "memory"
    LOGGER = "logger"
    MESSAGE_BUS = "message_bus"
    TOOL_MANAGER = "tool_manager"
    RUN_STORE = "run_store"