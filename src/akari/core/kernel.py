from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from akari.core.types import SubsystemName
from akari.execution.executor import TaskExecutor
from akari.execution.runtime_registry import RuntimeRegistry
from akari.execution.runtimes.callable_runtime import CallableRuntime
from akari.execution.runtimes.sklearn_runtime import SklearnRuntime
from akari.registry.registry import IdentityRegistry


@dataclass
class Kernel:
    """Core AKARI kernel.

    This is the central control-plane object that will coordinate all
    subsystems (registry, execution, policy, memory, observability, IPC, tools).

    At v0.0.2 this class still contains no real behaviour, but now exposes a
    minimal, stable API surface: accessors plus a describe_subsystems() helper.
    """

    # Placeholders for future subsystems (will gain concrete types later).
    registry: Optional[Any] = field(default=None, repr=False)
    executor: Optional[Any] = field(default=None, repr=False)
    policy_engine: Optional[Any] = field(default=None, repr=False)
    memory: Optional[Any] = field(default=None, repr=False)
    logger: Optional[Any] = field(default=None, repr=False)
    message_bus: Optional[Any] = field(default=None, repr=False)
    tool_manager: Optional[Any] = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        """
        Initialise default subsystems where appropriate.

        At v0.3.0 we attach:
        - IdentityRegistry (registry),
        - RuntimeRegistry + basic runtimes,
        - TaskExecutor wired to both.
        """
        # Registry
        if self.registry is None:
            self.registry = IdentityRegistry()

        # Runtime registry + runtimes
        runtime_registry = RuntimeRegistry()
        runtime_registry.register("callable", CallableRuntime())
        runtime_registry.register("sklearn", SklearnRuntime())

        # Executor
        if self.executor is None:
            self.executor = TaskExecutor(
                registry=self.registry,
                runtime_registry=runtime_registry,
            )

    # ---- Accessors -----------------------------------------------------

    def get_registry(self) -> Optional[Any]:
        """Return the registry subsystem, if configured."""
        return self.registry

    def get_executor(self) -> Optional[Any]:
        """Return the execution subsystem, if configured."""
        return self.executor

    def get_policy_engine(self) -> Optional[Any]:
        """Return the policy engine subsystem, if configured."""
        return self.policy_engine

    def get_memory(self) -> Optional[Any]:
        """Return the memory subsystem, if configured."""
        return self.memory

    def get_logger(self) -> Optional[Any]:
        """Return the observability / logging subsystem, if configured."""
        return self.logger

    def get_message_bus(self) -> Optional[Any]:
        """Return the IPC message bus subsystem, if configured."""
        return self.message_bus

    def get_tool_manager(self) -> Optional[Any]:
        """Return the tool manager subsystem, if configured."""
        return self.tool_manager

    # ---- Introspection -------------------------------------------------

    def describe_subsystems(self) -> Dict[str, Dict[str, str]]:
        """Describe the current state of all known subsystems.

        Returns:
            A mapping from subsystem name to a small summary dictionary,
            including whether it is present and which concrete type is used.

        This helper is intentionally simple and serialisable so it can be used
        in examples, tests and quick diagnostics.
        """

        def _describe(name: SubsystemName, value: Any) -> Dict[str, str]:
            is_present = value is not None
            type_name = type(value).__name__ if is_present else "None"
            return {
                "name": name.value,
                "present": "yes" if is_present else "no",
                "type": type_name,
            }

        return {
            SubsystemName.REGISTRY.value: _describe(
                SubsystemName.REGISTRY, self.registry
            ),
            SubsystemName.EXECUTOR.value: _describe(
                SubsystemName.EXECUTOR, self.executor
            ),
            SubsystemName.POLICY_ENGINE.value: _describe(
                SubsystemName.POLICY_ENGINE, self.policy_engine
            ),
            SubsystemName.MEMORY.value: _describe(
                SubsystemName.MEMORY, self.memory
            ),
            SubsystemName.LOGGER.value: _describe(
                SubsystemName.LOGGER, self.logger
            ),
            SubsystemName.MESSAGE_BUS.value: _describe(
                SubsystemName.MESSAGE_BUS, self.message_bus
            ),
            SubsystemName.TOOL_MANAGER.value: _describe(
                SubsystemName.TOOL_MANAGER, self.tool_manager
            ),
        }

    # ---- Syscall-like surface (still stubbed) --------------------------

    def submit_task(self, *args: Any, **kwargs: Any) -> Any:
        """Submit a task to the execution subsystem.

        For v0.0.2 this method is still a placeholder and will be properly
        implemented once the execution subsystem exists.
        """
        raise NotImplementedError(
            "Task submission is not implemented yet. "
            "This will be provided in v0.3.0 Task & Execution."
        )
