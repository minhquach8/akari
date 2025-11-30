# AKARI

An OS-style kernel and control-plane for AI systems.

This repository contains **AKARI** implementation, starting from a very small, config-first kernel and gradually adding subsystems for registry, execution, policy, memory, observability, IPC, and tools.

## Status: v0.2.0 – Kernel + Identity & Registry

Up to `v0.2.0`, AKARI provides:

- A **minimal kernel** (`Kernel`) that holds references to seven subsystems:
  `registry`, `executor`, `policy_engine`, `memory`, `logger`, `message_bus`, `tool_manager`, `run_store`.
- A **config-first** initialisation path via `AkariConfig` and `Kernel.from_config`.
- A `describe_subsystems()` helper for introspection.
- A **unified identity model** for:
  - models,
  - tools,
  - resources,
  - agents,
  - workspaces.
- An in-memory **IdentityRegistry** that:
  - stores specs (`ModelSpec`, `ToolSpec`, `ResourceSpec`, `AgentSpec`, `WorkspaceSpec`),
  - auto-generates canonical ids of the form `kind:slug`,
  - normalises names to slugs (e.g. `"Iris Classifier"` → `"iris_classifier"`),
  - preserves a human-friendly `display_name`,
  - supports smart lookups by id or “human-entered” names.

No external ML frameworks (scikit-learn, PyTorch, HuggingFace) are required or used at this stage; all examples use simple callables and metadata only.

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

At `v0.2.0` this includes:
- tests for kernel initialisation and describe_subsystems,
- tests for spec normalisation and IdentityRegistry lookups (id-based, human-name-based, disable, and list filtering).

## Examples

Two example scripts are provided so far:

### 1. 0.1.1 - Kernel Initialisation

```bash
python examples/usecase_0_1_1_kernel_initialisation.py
```

This will:
- create a default `AkariConfig`,
- build a `Kernel` via `Kernel.from_config(config)`,
- print a JSON overview of all subsystems, indicating whether each one is present and which concrete type (if any) is attached.

### 2. 0.2.1 - Identity & Registry basics

```bash
python examples/usecase_0_2_1_registry_basics.py
```

This demonstrates:
- creating a kernel with a default `IdentityRegistry`,
- registering:
  - a `ModelSpec` (e.g. “Iris Classifier”),
  - a `ToolSpec` (e.g. “Multiply Numbers”),
  - a `ResourceSpec` with a data path,
- inspecting canonical `id`, slug `name`, and `display_name`,
- resolving specs by:
  - canonical id (`"model:iris_classifier"`),
  - human-friendly names (`"Iris Classifier"`, `"iris classifier"`, `" IRIS Classifier "`).

## Project structure (v0.2.0)

High-level layout for this version:

``` text
pyproject.toml           # Project metadata, src-layout, pytest configuration
README.md                # Project overview, version status, and roadmap

src/
  akari/
    __init__.py          # Public API: exports Kernel and AkariConfig
    config.py            # AkariConfig shell (config-first initialisation)
    core/
      __init__.py
      kernel.py          # Kernel dataclass with subsystem slots + from_config
      types.py           # SubsystemName enum
    registry/
      __init__.py
      specs.py           # BaseSpec + ModelSpec, ToolSpec, ResourceSpec, AgentSpec, WorkspaceSpec
      registry.py        # IdentityRegistry: in-memory store and lookup
    execution/
      __init__.py        # Placeholder package for tasks & runtimes (v0.3.0+)
    policy/
      __init__.py        # Placeholder package for policy engine (v0.4.0+)
    memory/
      __init__.py        # Placeholder package for symbolic & vector memory (v0.5.0+)
    observability/
      __init__.py        # Placeholder package for logging & run tracking (v0.6.0+)
    ipc/
      __init__.py        # Placeholder package for message bus & agents (v0.7.0+)
    tools/
      __init__.py        # Placeholder package for tools & resources (v0.8.0+)

tests/
  test_kernel_initialisation.py      # Tests for Kernel.describe_subsystems
  test_registry_and_specs.py         # Tests for spec normalisation and IdentityRegistry behaviour

examples/
  usecase_0_1_1_kernel_initialisation.py  # Minimal kernel initialisation demo
  usecase_0_2_1_registry_basics.py        # Registry basics: model/tool/resource specs and lookups
```

## Roadmap

The implementation plan continues beyond `v0.2.0` with:

- **v0.3.0 – Tasks & Execution (Callable runtime first)**
Add `Task`, `TaskStatus`, `TaskResult`, a callable runtime, a `RuntimeRegistry`, and a TaskExecutor that dispatches purely based on spec.runtime. Policy and observability hooks are present but not yet enforced.

- **v0.4.0 – Policy (fail-closed)**
Integrate a `PolicyEngine` with deny-by-default semantics, wired into task execution and, later, memory and tools.

- **v0.5.0 – Memory & Knowledge (Symbolic + Vector)**
Implement symbolic and vector memory stores, governed by policy and observed through logging.

- **v0.6.0 – Observability & Run Tracking**
Introduce log/event sinks and experiment run tracking (in-memory and file-based backends).

- **v0.7.0 – IPC & Agents**
Add a message bus and a simple agent runtime for planner/worker patterns.

- **v0.8.0 – Tools & Resources**
Formalise tool definitions, tool runtimes (callable/http), and resource access with policy checks.

- **v0.9.0 – Userland Workspace & Mini-RAG**
Provide a higher-level `Workspace` façade, experiment helpers, and a small RAG-style workflow over the memory subsystem.

- **v1.0.0 – Integration Pack (PyTorch, HuggingFace, cross-framework demo)**
Optional runtimes for PyTorch and HuggingFace LLMs, configuration-driven registration, and a grand cross-framework example that ties together registry, execution, policy, memory, observability, IPC, and tools.

This repository tracks that progression step by step, keeping the kernel small, config-first, and framework-agnostic, while gradually adding subsystems around it.