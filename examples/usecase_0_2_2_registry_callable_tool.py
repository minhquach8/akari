"""
Use Case 0.2.2 – IdentityRegistry with a simple callable tool.

This example shows how to:

1. Create a Kernel (which initialises an IdentityRegistry by default).
2. Define a simple Python function as a tool.
3. Wrap it in a ToolSpec and register it with the registry.
4. Retrieve and inspect the registered spec.

There is deliberately no execution logic here yet; that will be handled by the Task / Execution subsystem in later versions.
"""

from __future__ import annotations

from typing import Any, Dict

from akari import Kernel
from akari.registry.specs import ToolSpec


def multiply(a: float, b: float) -> float:
    """Simple callable tool that multiplies two numbers."""
    return a * b


def main() -> None:
    """Entry point for the use case demonstration."""
    kernel = Kernel()
    registry = kernel.get_registry()
    assert registry is not None
    
    print("=== Use case 0.2.1 - Registry with callable tool ===\n")
    
    # 1. Create a ToolSpec for our multiply() function
    multiply_spec = ToolSpec(
        id="tool:multiply",
        name="Multiply two numbers",
        runtime="callable",
        metadata={"owner": "demo", "description": "Simple multiplication tool"},
        tags={"math", "demo"},
        binding=multiply,
    )
    
    # 2. Register the spec
    registry.register(multiply_spec)
    print("Registered tool spec:")
    print(f"  id  :  {multiply_spec.id}")
    print(f"  name:  {multiply_spec.name}")
    print(f"  kind:  {multiply_spec.kind.value}")
    print(f"  tags:  {sorted(multiply_spec.tags)}")

    # 3. Retrieve by id and by name
    fetched_by_id = registry.get("tool:multiply")
    fetched_by_name = registry.get("Multiply two numbers")
    
    print("Fetched by id == fetched by name? ", fetched_by_id is fetched_by_name)
    print("Fetched spec runtime:", fetched_by_id.runtime if fetched_by_id else "N/A")
    
    # Note: we do not actually call multiply() via a runtime yet.
    # That will be handled by the TaskExecutor and runtime layer in v0.3.x.


if __name__ == "__main__":
    main()