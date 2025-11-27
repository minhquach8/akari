from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Kernel:
    """
    Core AKARI kernel.

    This is the central control-plane object that will coordinate all
    subsystems (registry, execution, policy, memory, observability, IPC, tools).

    At v0.0.1 this class is just a skeleton. Subsystems will be added in later
    micro-versions.
    """
    registry: Optional[Any] = field(default=None, repr=False)
    executor: Optional[Any] = field(default=None, repr=False)
    policy_engine: Optional[Any] = field(default=None, repr=False)
    memory: Optional[Any] = field(default=None, repr=False)
    logger: Optional[Any] = field(default=None, repr=False)
    message_bus: Optional[Any] = field(default=None, repr=False)
    tool_manager: Optional[Any] = field(default=None, repr=False)
    
    
    def submit_task(self, *args: Any, **kwargs: Any) -> Any:
        """Submit a task to the execution subsystem.

        For v0.0.1 this method is a placeholder and will be properly implemented
        once the execution subsystem exists.
        """
        raise NotImplementedError(
            "Task submission is not implemented yet. "
            "This will be provided in v0.3.0 Task & Execution."
        )