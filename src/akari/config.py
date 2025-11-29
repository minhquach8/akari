from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class AkariConfig:
    """
    Configuration shell for initialising an AKARI Kernel.
    
    At v0.1.0 this is intentionally minimal and mostly acts as a structured placeholder. Later versions will use this to wire concrete backends.
    """
    
    logging_backend: str = "in-memory"
    runstore_backend: str = "in-memory"
    policy_source: Optional[str] = None
    runtime_table: Dict[str, str] = field(default_factory=dict)
    artefact_base_path: Optional[Path] = None
    

    @classmethod
    def from_path(cls, path: str | Path) -> AkariConfig:
        """
        Load configuration from a file path.
        
        At v0.1.0, this method only supports a very thin stub implementaion. In later versions, it will parse YAML or TOML.
        """
        # For now we simply ignore the content and return defaults.
        # The method exists so that Kernel.from_config can already accept paths.
        return cls()
    