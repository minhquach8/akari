"""Tests for basic kernel initialisation and subsystem description."""

from akari import Kernel
from akari.core.types import SubsystemName


def test_kernel_initialisation_has_all_subsystems() -> None:
    """Kernel.describe_subsystems should expose all known subsystems."""
    kernel = Kernel()
    description = kernel.describe_subsystems()

    # Expected keys come directly from the SubsystemName enum.
    expected_keys = {name.value for name in SubsystemName}
    assert set(description.keys()) == expected_keys

    # Each entry should have a simple, consistent structure.
    for key, info in description.items():
        assert "name" in info, f"Subsystem '{key}' is missing 'name'"
        assert "present" in info, f"Subsystem '{key}' is missing 'present'"
        assert "type" in info, f"Subsystem '{key}' is missing 'type'"

        # Ensure the 'name' field matches the dictionary key.
        assert info["name"] == key
        # 'present' must be a simple yes/no flag as a string.
        assert info["present"] in {"yes", "no"}
        # 'type' is a human-readable type name.
        assert isinstance(info["type"], str)
