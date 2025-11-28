"""
Use Case 0.1.1 – Kernel initialisation overview.

This example demonstrates how to create a Kernel instance and inspect its subsystems using describe_subsystems(). At v0.0.4 all subsystems are still unconfigured (None), but the control-plane surface is already in place.
"""

from __future__ import annotations

import json
from typing import Any, Dict

from akari import Kernel


def format_subsystems_as_table(description: Dict[str, Dict[str, Any]]) -> str:
    lines: list[str] = []
    header = f"{'Subsystem':<15} {'Present':<10} {'Type'}"
    separator = "-" * len(header)
    lines.append(header)
    lines.append(separator)
    
    for name, info in description.items():
        present = info.get("present", "?")
        type_name = info.get("type", "?")
        lines.append(f"{name:<15} {present:<10} {type_name}")
        
    return "\n".join(lines)


def main() -> None:
    kernel = Kernel()
    description = kernel.describe_subsystems()
    
    print("=== AKARI Kernel Initialisation (Use Case 0.1.1) ===\n")
    
    print("Subsystem overview:")
    print(format_subsystems_as_table(description))
    print()
    
    print("Raw description (JSON):")
    print(json.dumps(description, indent=2))
    
if __name__ == "__main__":
    main()