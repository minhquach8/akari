"""
Identity registry subsystem.

This package provides specifications (ModelSpec, AgentSpec, ToolSpec, ResourceSpec, WorkspaceSpec) and the in-memory IdentityRegistry used to store, retrieve, and manage all identifiable entities in the AKARI runtime.

The registry does not execute models or tools; it only manages identity, metadata, runtime declarations, and lookup.

Runtime execution is delegated to the execution subsystem.
"""
