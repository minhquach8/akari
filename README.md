# AKARI — AI Control-Plane Kernel (v1.0.0)

**AKARI** is an experimental **AI control-plane kernel** designed to coordinate models, agents, tools, memory, and policies across heterogeneous ML frameworks (sklearn, PyTorch, HuggingFace, callable tools…).

Think of AKARI as:

> **An operating system for AI workflows, not for hardware.**
> It organises *AI models, agents, tasks, tools, memory, and safety policies* the way a traditional OS organises *processes, files, memory, and drivers*.

AKARI provides:

* A **small, stable kernel**
* A **typed identity registry**
* A **runtime driver model**
* A **policy engine (fail-closed)**
* **Symbolic + vector memory stores**
* **Observability & experiment tracking**
* **IPC-based agent runtime**
* A unified **Workspace** façade for userland workflows

This repository contains a full v1.0.0 reference implementation, including tests and end-to-end examples.

---

## Core Concepts

### 1. **Kernel**

Central orchestrator providing:

* Registry
* Task execution
* Policy engine
* Memory subsystem
* Observability (logs + runs)
* Message bus
* Tool manager

Everything goes through the kernel.

---

### 2. **Identity Registry**

Typed specs:

* `ModelSpec`
* `AgentSpec`
* `ToolSpec`
* `ResourceSpec`
* `WorkspaceSpec`

Each spec has:

* `id`
* `name`
* `kind`
* `runtime`
* `tags`
* `binding`
* lifecycle fields (`enabled`, metadata)

---

### 3. **Execution Engine**

Uses the **runtime driver model**:

| Runtime string | Driver class            |
| -------------- | ----------------------- |
| `"callable"`   | `CallableRuntime`       |
| `"sklearn"`    | `SklearnRuntime`        |
| `"pytorch"`    | `PytorchRuntime`        |
| `"hf-llm"`     | `HuggingFaceLLMRuntime` |

Selection is based solely on **spec.runtime** → no reflection, no guessing.

---

### 4. **Policy Engine (Fail-Closed)**

AKARI enforces **deny-by-default** safety:

* `model.invoke`
* `tool.invoke`
* `memory.write`
* `memory.read`
* `resource.access`

If no rule matches → **DENY**.

Policies use:

* `PolicyRule`
* `PolicyCondition`
* `PolicySet`
* YAML/JSON loading supported.

---

### 5. **Memory Subsystem**

Two complementary stores:

#### Symbolic memory

* Append-only notes
* Query by metadata or substring
* Classification & version fields
* Policy-controlled

#### Vector memory

* Embedding-based semantic search
* Pluggable `EmbeddingFunction`
* API: `index_vector`, `search_vector`

---

### 6. **Observability**

* `LogEvent` + `LogStore`

  * In-memory
  * JSON Lines persistent backend
* `ExperimentRun` + `RunStore`

  * In-memory
  * JSON persistent backend

Events include:

* `task.created`
* `task.started`
* `task.completed`
* `task.failed`
* `policy.allowed`
* `policy.denied`
* `memory.write`
* `memory.read`

Runs store:

* parameters
* metrics
* artefacts
* timestamps

---

### 7. **IPC & Agent Runtime**

* In-memory message bus
* `AgentRuntime` event loop
* Planner/worker pattern built-in
* Tasks flow through IPC, kernel, policies, runtimes

---

### 8. **Tools & Resources**

* `ToolDefinition`, `ToolRuntime`, `ToolInvocationResult`
* `CallableToolRuntime`
* `HttpToolRuntime`
* File/URI resources with policy enforcement

---

### 9. **Workspace (Userland)**

High-level façade for:

* Registering models
* Running models
* Logging notes
* Semantic search
* Experiment tracking
* Mini-RAG workflows
* Using tools
* Reading system logs

Provides:

* `experiment_run(...)` context manager
* `autolog_experiment` decorator

---

## Project Structure

```
akari/
 ├── core/               # Kernel and core types
 ├── registry/           # Identity registry + specs
 ├── execution/          # Task executor + runtimes
 ├── policy/             # Policy engine + loader
 ├── memory/             # Symbolic + vector memory
 ├── observability/      # Logging + run tracking
 ├── ipc/                # Message bus + agent runtime
 ├── tools/              # Tool subsystem
 └── userland/           # Workspace, experiments
```

---

## Quickstart

Install:

```bash
pip install -r requirements.txt
```

Run a simple task:

```python
from akari import Kernel
from akari.registry.specs import ToolSpec

kernel = Kernel()
registry = kernel.get_registry()
executor = kernel.get_executor()

def add(a, b): return a + b

registry.register(ToolSpec(
    id="tool:add",
    name="Add numbers",
    kind="tool",
    runtime="callable",
    binding=add,
))

task = {
    "subject": "user:demo",
    "target_id": "tool:add",
    "input": {"a": 20, "b": 22},
}

result = executor.run_task_dict(task)
print(result.output)  # → 42
```

---

## Test Suite

The project includes **dozens of unit tests** covering:

* specs & registry
* runtime registry
* sklearn / pytorch / HF runtimes
* task lifecycle
* policy engine
* symbolic & vector memory
* observability logs & run tracking
* IPC & agent runtime
* tool subsystem
* Workspace full workflows

Run all tests:

```bash
pytest -q
```

---

## Key Examples

All examples are under `examples/`:

### 0.x examples (foundation)

* registry fundamentals
* tasks and runtimes
* policy allow/deny
* memory read/write
* vector search
* IPC ping-pong

### 1.x examples (production integration)

* **1.0.1 – PyTorch ResNet18 runtime**
* **1.0.2 – HuggingFace LLM runtime**
* **1.0.3 – Grand unified cross-framework pipeline**

  * sklearn + pytorch + HF
  * planner/worker agents
  * vector & symbolic memory
  * rule-engine tool
  * fail-closed policy

### config example

* **1.0.0 – Kernel.from_config**

  * boot Kernel from `akari.yml`
  * persistent logs + run store

---

## Configuration

AKARI supports structured config via `AkariConfig`:

* log backend
* runstore backend
* policy files
* runtime settings (HF device/mps/cuda, dtype, etc.)

Load with:

```python
from akari import Kernel
kernel = Kernel.from_config("akari.yml")
```

---

## Architectural Philosophy

AKARI follows four principles:

### 1. **Small kernel, large userland**

Keep the kernel minimal, predictable, composable.

### 2. **Driver model for runtimes**

sklearn, torch, HF, callable, HTTP → all mapped via runtime strings.

### 3. **Fail-closed safety by default**

No rule → deny.

### 4. **Everything observable**

Tasks, policies, memory, runs → all logged.

---

## Roadmap

* v1.1 – remote agents + gRPC message bus
* v1.2 – sandboxed tool runner
* v1.3 – distributed run tracking
* v1.4 – improved config (multiple kernels per node)
* v2.x – cluster-scale AI-OS architecture

---

## Contributing

PRs are welcome.
Design philosophy follows:
**clean interfaces → strong invariants → predictable behaviour**.

---

## Licence

MIT License.

---