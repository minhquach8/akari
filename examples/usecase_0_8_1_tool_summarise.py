"""Use Case 0.8.1 – Summarise tool via ToolManager."""

from __future__ import annotations

from akari import Kernel
from akari.registry.specs import ToolSpec


def summarise_text(text: str, max_chars: int = 40) -> str:
    """Very simple summarise function by string slicing."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def main() -> None:
    kernel = Kernel()
    registry = kernel.get_registry()
    tool_manager = kernel.get_tool_manager()

    # Register summarise tool.
    spec = ToolSpec(
        id="tool:summarise",
        name="Summarise text (string slice)",
        runtime="callable",
        binding=summarise_text,
        tags={"demo", "text"},
    )
    registry.register(spec)

    text = "AKARI is an AI control-plane kernel focused on safety and observability."
    print("=== Use Case 0.8.1 – Summarise tool ===\n")
    print("Original:", text)

    result = tool_manager.invoke(
        tool_id="tool:summarise",
        arguments={"text": text, "max_chars": 50},
        subject="user:demo",
    )

    print("\nInvocation success:", result.success)
    print("Output:", result.output)
    if result.error:
        print("Error:", result.error)


if __name__ == "__main__":
    main()
