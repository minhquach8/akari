"""
Task execution subsystem.

This package contains abstractions for Tasks, TaskStatus, TaskResult, runtime implementations (callable, sklearn, PyTorch, HuggingFace, etc.), and the TaskExecutor responsible for dispatching tasks to the appropriate runtime based on the spec.runtime declaration.

Execution does not store identity (registry) and does not enforce policies. Policy checks, observability logging, and memory access must be mediated through the Kernel.
"""
