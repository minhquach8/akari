# AKARI

An OS-style kernel and control-plane for AI systems.

This repository contains **AKARI** implementation, starting from a very small, config-first kernel and gradually adding subsystems for registry, execution, policy, memory, observability, IPC, and tools.

## Status: v0.1.0 – Kernel Skeleton

This version defines the **shape** of AKARI, but does not yet execute any models or tools. The goals of `v0.1.0` are:

- A minimal project skeleton using `src/` layout.
- A `Kernel` type that holds references to seven subsystems:
  `registry`, `executor`, `policy_engine`, `memory`, `logger`, `message_bus`, `tool_manager`, `run_store`.
- A config-first initialisation path via `AkariConfig` and `Kernel.from_config`.
- A `describe_subsystems()` helper for introspection.
- A basic test and a small example script to verify that the kernel can be created and inspected.

No external ML frameworks (scikit-learn, PyTorch, HuggingFace) are required or used at this stage.

## Installation

AKARI uses a standard Python `src/` layout and can be installed in editable mode for development.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -e .
```

## Running tests

After installation, you can run the initial test suite:

```bash
pytest
```

## Examples

The first example demonstrates kernel initialisation and subsystem overview:

```bash
python examples/usecase_0_1_1_kernel_initialisation.py
```

This will:
- create a default AkariConfig,
- build a Kernel via Kernel.from_config(config),
- print a JSON overview of all subsystems, indicating whether each one is present and which concrete type (if any) is attached.

## Project structure (v0.1.0)

High-level layout for this version:

```text
pyproject.toml           # Project metadata, src-layout, pytest configuration
README.md                # This file

src/
  akari/
    __init__.py          # Public API: exports Kernel and AkariConfig
    config.py            # AkariConfig shell (config-first initialisation)
    core/
      __init__.py
      kernel.py          # Kernel dataclass with subsystem slots
      types.py           # SubsystemName enum
    registry/
      __init__.py        # Placeholder package for identity & specs
    execution/
      __init__.py        # Placeholder package for tasks & runtimes
    policy/
      __init__.py        # Placeholder package for policy engine
    memory/
      __init__.py        # Placeholder package for symbolic & vector memory
    observability/
      __init__.py        # Placeholder package for logging & run tracking
    ipc/
      __init__.py        # Placeholder package for message bus & agents
    tools/
      __init__.py        # Placeholder package for tools & resources

tests/
  test_kernel_initialisation.py  # Tests for Kernel.describe_subsystems

examples/
  usecase_0_1_1_kernel_initialisation.py  # Minimal kernel initialisation demo
```

## Roadmap

The implementation plan continues beyond `v0.1.0` with:

- **v0.2.0 – Identity & Registry**  
  Introduce spec models (`ModelSpec`, `ToolSpec`, `ResourceSpec`, `AgentSpec`, `WorkspaceSpec`) and an in-memory `IdentityRegistry`.

- **v0.3.0 – Tasks & Execution**  
  Add `Task`, `TaskResult`, a callable runtime, and a `TaskExecutor` that dispatches purely based on `spec.runtime`.

- **v0.4.0 – Policy (fail-closed)**  
  Integrate a `PolicyEngine` with deny-by-default semantics, wired into task execution.

- ... and further versions for memory, observability, IPC, tools, and userland
  workspace.

This repository tracks that progression step by step, keeping the kernel small, config-first, and framework-agnostic.