"""
Memory subsystem (symbolic and vector).

This package provides the abstractions and stores for symbolic memory (MemoryRecord, channels, metadata filtering) and vector memory (embeddings, semantic search).

Memory access is subject to policy control; read/write/index/search operations are mediated by the Kernel to ensure governance, safety, and reproducibility.

Both symbolic and vector stores are designed to be replaceable with different backends in later versions.
"""
