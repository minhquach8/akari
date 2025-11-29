"""Tests for Kernel integration with the IdentityRegistry."""

from akari import Kernel
from akari.core.types import SubsystemName
from akari.registry.registry import IdentityRegistry


def test_kernel_initialises_identity_registry_by_default() -> None:
    """Kernel should create an IdentityRegistry when no registry is provided."""
    kernel = Kernel()
    
    registry = kernel.get_registry()
    assert isinstance(registry, IdentityRegistry)
    
    description = kernel.describe_subsystems()
    registry_info = description[SubsystemName.REGISTRY.value]
    
    assert registry_info["present"] == "yes"
    assert registry_info["type"] == "IdentityRegistry"