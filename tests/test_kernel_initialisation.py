from akari import Kernel
from akari.core.types import SubsystemName


def test_kernel_describe_susbsystems_has_all_entries() -> None:
    kernel = Kernel()
    description = kernel.describe_subsystems()
    
    # Ensure all expected subsystems are present as keys
    for name in SubsystemName:
        assert name.value in description
        
    # Ensure each entry is a dict with required fields
    for entry in description.values():
        assert "present" in entry
        assert "type" in entry