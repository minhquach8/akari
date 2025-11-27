"""Shared core types and constants for the AKARI kernel."""

from __future__ import annotations

from enum import Enum


class SubsystemName(str, Enum):
    """Canonical names for AKARI kernel subsystems."""

    REGISTRY = "registry"
    EXECUTOR = "executor"
    POLICY_ENGINE = "policy_engine"
    MEMORY = "memory"
    LOGGER = "logger"
    MESSAGE_BUS = "message_bus"
    TOOL_MANAGER = "tool_manager"