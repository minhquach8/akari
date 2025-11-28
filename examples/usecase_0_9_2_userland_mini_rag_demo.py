"""Use Case 0.9.2 – Mini RAG demo via Workspace + ToolManager."""

from __future__ import annotations

from akari import Kernel
from akari.registry.specs import ToolSpec
from akari.userland.workspace import Workspace


def summarise_text(text: str, max_chars: int = 80) -> str:
    """Simple summariser by slicing."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + '...'


def main() -> None:
    kernel = Kernel()
    workspace = Workspace('workspace:rag', kernel)
    registry = kernel.get_registry()

    print('=== Use Case 0.9.2 – Mini RAG demo ===\n')

    # 1. Register summarise tool.
    summarise_spec = ToolSpec(
        id='tool:summarise',
        name='Summarise text',
        runtime='callable',
        binding=summarise_text,
        tags={'demo', 'text'},
    )
    registry.register(summarise_spec)
    print("Registered tool 'tool:summarise'.")

    # 2. Index documents into vector memory.
    docs = [
        (
            'doc1',
            'AKARI is an AI control-plane kernel that coordinates models, '
            'agents, tools and memory with strong safety guarantees.',
        ),
        (
            'doc2',
            'Explainable AI techniques help researchers and clinicians '
            'interpret machine learning models.',
        ),
        (
            'doc3',
            'Reproducible experiment tracking is essential for trustworthy '
            'machine learning pipelines.',
        ),
    ]

    for doc_id, text in docs:
        workspace.index_document(
            channel='docs',
            text=text,
            metadata={'doc_id': doc_id},
        )
    print('Indexed 3 documents into vector memory.\n')

    # 3. Semantic search.
    query = 'interpretability of models'
    print(f'Query: {query}\n')
    results = workspace.search_documents(
        channel='docs',
        query_text=query,
        top_k=2,
    )

    print('Top retrieved documents:')
    combined_texts = []
    for rec, score in results:
        doc_id = rec.metadata.get('doc_id')
        text = rec.text
        combined_texts.append(f'[{doc_id}] {text}')
        print(f'- [{doc_id}] (score={score:.3f}) {text}')

    # 4. Summarise retrieved content via tool.
    full_context = '\n'.join(combined_texts)
    tool_result = workspace.call_tool(
        tool_id='tool:summarise',
        arguments={'text': full_context, 'max_chars': 200},
    )

    print('\nSummarised answer:')
    if tool_result.success:
        print(tool_result.output)
    else:
        print('Tool invocation failed:', tool_result.error)

    print('\nMini RAG demo completed.')


if __name__ == '__main__':
    main()
