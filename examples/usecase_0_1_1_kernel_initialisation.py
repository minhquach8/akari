from __future__ import annotations

import json

from akari import AkariConfig, Kernel


def main() -> None:
    config = AkariConfig()
    kernel = Kernel.from_config(config)
    
    print("AKARI Kernel initialised.")
    print("Subsystem overview:")
    
    description = kernel.describe_subsystems()
    print(json.dumps(description, indent=2, sort_keys=True))
    
    
if __name__ == "__main__":
    main()