from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from akari.config import AkariConfig
from akari.core.types import SubsystemName
from akari.registry.registry import IdentityRegistry


@dataclass
class Kernel:
    """
    Core AKARI Kernel holding references to subsystems.

    At v0.1.0 all subsystems are optional and may be None. Later versions will gradually replace these with concrete implementations.

    The kernel itself stays intentionally small and stable.
    """

    registry: Any = None
    executor: Any = None
    policy_engine: Any = None
    memory: Any = None
    logger: Any = None
    message_bus: Any = None
    tool_manager: Any = None
    run_store: Any = None

    config: Optional[AkariConfig] = field(default=None, repr=False)

    def get_registry(self) -> Any:
        """Return the registry subsystem"""
        return self.registry

    def get_executor(self) -> Any:
        """Return the task executor subsystem"""
        return self.executor

    def get_policy_engine(self) -> Any:
        """Return the policy engine subsystem"""
        return self.policy_engine

    def get_memory(self) -> Any:
        """Return the memory subsystem."""
        return self.memory

    def get_logger(self) -> Any:
        """Return the logging subsystem."""
        return self.logger

    def get_message_bus(self) -> Any:
        """Return the IPC/message bus subsystem."""
        return self.message_bus

    def get_tool_manager(self) -> Any:
        """Return the tool manager subsystem."""
        return self.tool_manager

    def get_run_store(self) -> Any:
        """Return the run store subsystem."""
        return self.run_store

    def describe_subsystems(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a lightweight description of all subsystems.
        
        This is mainly for debugging, examples, and tests. It should remain safe to call even when the kernel is only partially initialised.
        """
        return {
            SubsystemName.REGISTRY.value: {
                "present": self.registry is not None,
                "type": type(self.registry).__name__ if self.registry is not None else None,
            },
            SubsystemName.EXECUTOR.value: {
                "present": self.executor is not None,
                "type": type(self.executor).__name__ if self.executor is not None else None,
            },
            SubsystemName.POLICY_ENGINE.value: {
                "present": self.policy_engine is not None,
                "type": type(self.policy_engine).__name__ if self.policy_engine is not None else None,
            },
            SubsystemName.MEMORY.value: {
                "present": self.memory is not None,
                "type": type(self.memory).__name__ if self.memory is not None else None,
            },
            SubsystemName.LOGGER.value: {
                "present": self.logger is not None,
                "type": type(self.logger).__name__ if self.logger is not None else None,
            },
            SubsystemName.MESSAGE_BUS.value: {
                "present": self.message_bus is not None,
                "type": type(self.message_bus).__name__ if self.message_bus is not None else None,
            },
            SubsystemName.TOOL_MANAGER.value: {
                "present": self.tool_manager is not None,
                "type": type(self.tool_manager).__name__ if self.tool_manager is not None else None,
            },
            SubsystemName.RUN_STORE.value: {
                "present": self.run_store is not None,
                "type": type(self.run_store).__name__ if self.run_store is not None else None,
            },
        }
        
    @classmethod
    def from_config(
        cls,
        config_or_path: AkariConfig | str | Path | None = None,
    ) -> Kernel:
        """
        Construct a Kernel from an AkariConfig or a config file path.
        
        At v0.1.0 this mostly wires an empty kernel and attaches the config object for later use.
        """ 
        if config_or_path is None:
            config = AkariConfig()
        elif isinstance(config_or_path, (str, Path)):
            config = AkariConfig.from_path(config_or_path)
        else:
            config = config_or_path
            
        # Future versions will instantiate concrete subsystems based on config.
        return cls(
            registry=IdentityRegistry(),
            executor=None,
            policy_engine=None,
            memory=None,
            logger=None,
            message_bus=None,
            tool_manager=None,
            run_store=None,
            config=config,
        )