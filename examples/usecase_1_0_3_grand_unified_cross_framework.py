"""
Use Case 1.0.3 – Grand unified cross-framework pipeline.

This example demonstrates how AKARI can orchestrate:
- A sklearn SVM model (Iris classifier),
- A small PyTorch model,
- A HuggingFace summariser (HF-LLM runtime),
- A rule-engine tool (callable tool),
- Symbolic and vector memory,

all through a single Kernel, using the existing execution, tools and memory
subsystems.

For simplicity, this example runs the steps sequentially in one process.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
from sklearn import datasets, svm
from transformers import pipeline

from akari import Kernel
from akari.execution.runtimes.hf_llm_runtime import HuggingFaceLLMRuntime
from akari.execution.runtimes.pytorch_runtime import PytorchRuntime
from akari.execution.task import Task
from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet
from akari.registry.specs import ModelSpec, ToolSpec

# ---------------------------------------------------------------------------
# Helper builders for models and tools
# ---------------------------------------------------------------------------


def build_iris_svm_model() -> svm.SVC:
    """Train a simple SVM classifier on the Iris dataset."""
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    clf = svm.SVC(kernel='linear', probability=True, random_state=0)
    clf.fit(X, y)
    return clf


def build_torch_demo_model() -> torch.nn.Module:
    """Build a tiny PyTorch model for demonstration.

    We use a single linear layer mapping R^4 -> R^3 to roughly match
    the Iris feature space shape, but this is not a trained model.
    """
    model = torch.nn.Sequential(
        torch.nn.Linear(4, 16),
        torch.nn.ReLU(),
        torch.nn.Linear(16, 3),
    )
    # In a real scenario you would load trained weights here.
    return model


def build_hf_summariser() -> Any:
    """Create a HuggingFace summarisation pipeline.

    This reuses the same idea as Use Case 1.0.2. The actual model may be
    large and take time to download the first time.
    """
    summariser = pipeline('summarization')
    return summariser


def rule_engine(summary: str, svm_class: int) -> str:
    """Very simple rule engine over the summary and SVM prediction.

    This is intentionally trivial: it reads the SVM predicted class
    and attaches a 'risk' label for demonstration only.
    """
    if svm_class == 2:
        risk = 'high-risk pattern detected (class 2).'
    elif svm_class == 1:
        risk = 'moderate-risk pattern detected (class 1).'
    else:
        risk = 'low-risk pattern detected (class 0).'

    return f'{summary.strip()}  [RuleEngine: {risk}]'


# ---------------------------------------------------------------------------
# Registry wiring – register all components into AKARI
# ---------------------------------------------------------------------------


def register_cross_framework_components(kernel: Kernel) -> Dict[str, str]:
    """Register sklearn, PyTorch, HF and rule-engine tool in the registry.

    Returns:
        A mapping from logical names to spec ids.
    """
    registry = kernel.get_registry()

    # 1. Sklearn Iris SVM
    iris_svm = build_iris_svm_model()
    iris_spec = ModelSpec(
        id='model:iris_svm',
        name='Iris SVM classifier (sklearn)',
        runtime='sklearn',
        binding=iris_svm,
        tags={'demo', 'iris', 'sklearn'},
        metadata={},
    )
    registry.register(iris_spec)

    # 2. PyTorch demo model
    torch_model = build_torch_demo_model()
    torch_spec = ModelSpec(
        id='model:torch_demo',
        name='Demo PyTorch model',
        runtime='pytorch',
        binding=torch_model,
        tags={'demo', 'pytorch'},
        metadata={},
    )
    registry.register(torch_spec)

    # 3. HF summariser (pipeline) – bound to 'hf-llm' runtime
    summariser = build_hf_summariser()
    hf_spec = ModelSpec(
        id='model:hf_summariser',
        name='HF summariser',
        runtime='hf-llm',
        binding=summariser,
        tags={'demo', 'hf', 'summariser'},
        metadata={},
    )
    registry.register(hf_spec)

    # 4. Rule-engine tool as a callable tool
    rule_tool_spec = ToolSpec(
        id='tool:rule_engine',
        name='Simple rule-engine over summary + class',
        runtime='callable',
        binding=rule_engine,
        tags={'demo', 'rule-engine'},
        metadata={},
    )
    registry.register(rule_tool_spec)

    return {
        'iris_model': iris_spec.id,
        'torch_model': torch_spec.id,
        'hf_summariser': hf_spec.id,
        'rule_tool': rule_tool_spec.id,
    }


# ---------------------------------------------------------------------------
# Memory initialisation – symbolic notes + vector documents
# ---------------------------------------------------------------------------


def seed_memory(kernel: Kernel) -> None:
    """Seed both symbolic and vector memory with small demo content."""
    memory = kernel.get_memory()
    subject = 'agent:planner'

    # Symbolic notes in a 'notes' channel
    memory.write_symbolic(
        channel='notes',
        record_id='notes:1',
        content='Patient cohort: demo synthetic case using Iris-like features.',
        subject=subject,
        metadata={'topic': 'demo', 'kind': 'note'},
        classification='internal',
    )

    # Vector documents in a 'docs' channel
    docs: List[Tuple[str, str]] = [
        ('doc1', 'Class 0 in Iris is usually setosa and often considered low risk.'),
        ('doc2', 'Class 1 in Iris is versicolor; moderate complexity in the dataset.'),
        (
            'doc3',
            'Class 2 in Iris is virginica and sometimes used as a proxy for harder cases.',
        ),
    ]

    for doc_id, text in docs:
        memory.index_vector(
            channel='docs',
            record_id=f'docs:{doc_id}',
            text=text,
            subject=subject,
            metadata={'doc_id': doc_id, 'topic': 'iris'},
        )


# ---------------------------------------------------------------------------
# Grand unified pipeline
# ---------------------------------------------------------------------------


def run_grand_pipeline(kernel: Kernel, ids: Dict[str, str]) -> None:
    """Run the unified pipeline across sklearn, PyTorch, HF and tools."""
    executor = kernel.get_executor()
    memory = kernel.get_memory()
    tool_manager = kernel.get_tool_manager()

    subject = 'agent:planner'
    workspace = 'workspace:grand-demo'

    print('=== Use Case 1.0.3 – Grand unified cross-framework pipeline ===\n')

    # ------------------------------------------------------------------
    # Step 1 – Sklearn SVM prediction on Iris sample
    # ------------------------------------------------------------------
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    sample_index = 0
    sample_features = X[sample_index].reshape(1, -1)
    true_class = int(y[sample_index])

    iris_task = Task(
        id='task:iris_svm:demo',
        subject=subject,
        workspace=workspace,
        target_id=ids['iris_model'],
        input=sample_features,
    )
    iris_result = executor.run(iris_task)

    predicted_class = int(iris_result.output[0])
    print('Sklearn SVM prediction:')
    print(f'  Features      : {sample_features.tolist()}')
    print(f'  True class    : {true_class}')
    print(f'  Predicted     : {predicted_class}\n')

    # ------------------------------------------------------------------
    # Step 2 – PyTorch demo model on the same features (converted to tensor)
    # ------------------------------------------------------------------
    features_tensor = torch.tensor(sample_features, dtype=torch.float32)

    torch_task = Task(
        id='task:torch_demo:demo',
        subject=subject,
        workspace=workspace,
        target_id=ids['torch_model'],
        input=features_tensor,
    )
    torch_result = executor.run(torch_task)

    torch_output = torch_result.output
    if isinstance(torch_output, torch.Tensor):
        torch_output_repr = torch_output.detach().cpu().numpy().tolist()
    else:
        torch_output_repr = torch_output
    print('PyTorch demo model output:')
    print(f'  Raw output    : {torch_output_repr}\n')

    # ------------------------------------------------------------------
    # Step 3 – Retrieve contextual documents from vector memory
    # ------------------------------------------------------------------
    search_results = memory.search_vector(
        channel='docs',
        query_text=f'iris class {predicted_class} risk',
        subject=subject,
        top_k=2,
    )

    combined_context_parts: List[str] = []
    print('Top retrieved documents from vector memory:')
    for rec, score in search_results:
        doc_id = rec.metadata.get('doc_id')
        text = rec.text
        combined_context_parts.append(f'[{doc_id}] {text}')
        print(f'  - [{doc_id}] (score={score:.3f}) {text}')
    print()

    combined_context = '\n'.join(combined_context_parts)

    # ------------------------------------------------------------------
    # Step 4 – Build a long text and summarise via HF-LLM runtime
    # ------------------------------------------------------------------
    long_text = (
        'AKARI grand demo: we combined sklearn SVM prediction, a PyTorch model output '
        'and retrieved documents from vector memory to form a unified view.\n\n'
        f'Sklearn predicted class: {predicted_class} (true: {true_class}).\n'
        f'PyTorch demo output: {torch_output_repr}.\n\n'
        f'Context documents:\n{combined_context}\n'
    )

    hf_task = Task(
        id='task:hf_summariser:demo',
        subject=subject,
        workspace=workspace,
        target_id=ids['hf_summariser'],
        input=long_text,
    )
    hf_result = executor.run(hf_task)

    # HF output is a list[dict], similar to Use Case 1.0.2.
    hf_output = hf_result.output
    if isinstance(hf_output, list) and hf_output and isinstance(hf_output[0], dict):
        summary_text = hf_output[0].get('summary_text', '')
    else:
        summary_text = str(hf_output)

    print('HF summariser output:')
    print(f'  Summary       : {summary_text}\n')

    # ------------------------------------------------------------------
    # Step 5 – Apply rule-engine tool via ToolManager
    # ------------------------------------------------------------------
    rule_result = tool_manager.invoke(
        subject=subject,
        tool_id=ids['rule_tool'],
        arguments={'summary': summary_text, 'svm_class': predicted_class},
    )

    print('Rule-engine tool result:')
    print(f'  Success       : {rule_result.success}')
    print(f'  Output        : {rule_result.output}')
    print(f'  Error         : {rule_result.error}\n')

    # ------------------------------------------------------------------
    # Optional – demonstrate policy denial for a different subject
    # ------------------------------------------------------------------
    intruder_subject = 'agent:intruder'
    denied_task = Task(
        id='task:iris_svm:intruder',
        subject=intruder_subject,
        workspace=workspace,
        target_id=ids['iris_model'],
        input=sample_features,
    )
    denied_result = executor.run(denied_task)

    print('Policy denial demo (intruder trying to invoke model):')
    print(f'  Subject       : {intruder_subject}')
    print(f'  Task status   : {denied_result.status}')
    print(f'  Error         : {denied_result.error}\n')

    print('Grand unified cross-framework pipeline completed.')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def ensure_artifacts_dirs() -> None:
    os.makedirs('artifacts', exist_ok=True)


def build_kernel() -> Kernel:
    """Build a Kernel instance with a real PolicyEngine for the grand demo."""
    ensure_artifacts_dirs()
    policy_engine = build_policy_engine_for_grand_demo()
    return Kernel(policy_engine=policy_engine)


def build_policy_engine_for_grand_demo() -> PolicyEngine:
    """Build a simple fail-closed policy for the grand demo.

    Only agent:planner is allowed to:
    - invoke any model,
    - invoke any tool,
    - read/write any memory channel.

    All other subjects are denied by default (fail-closed).
    """
    rules = [
        PolicyRule(
            id='allow-planner-model-invoke',
            description='Allow planner to invoke any model',
            subject_match='agent:planner',
            action='model.invoke',
            resource_match='*',
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id='allow-planner-tool-invoke',
            description='Allow planner to invoke any tool',
            subject_match='agent:planner',
            action='tool.invoke',
            resource_match='*',
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id='allow-planner-memory-write',
            description='Allow planner to write any memory channel',
            subject_match='agent:planner',
            action='memory.write',
            resource_match='*',
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id='allow-planner-memory-read',
            description='Allow planner to read any memory channel',
            subject_match='agent:planner',
            action='memory.read',
            resource_match='*',
            effect=PolicyEffect.ALLOW,
        ),
    ]

    policy_set = PolicySet(name='grand-demo-policy', rules=rules, version='v1')
    return PolicyEngine(policy_set)


def main() -> None:
    kernel = build_kernel()

    # Register all models and tools
    ids = register_cross_framework_components(kernel)

    # Seed memory with notes and documents
    seed_memory(kernel)

    # Run the grand unified pipeline
    run_grand_pipeline(kernel, ids)


if __name__ == '__main__':
    main()
