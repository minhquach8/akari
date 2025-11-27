"""
Tool and resource subsystem.

This package defines tool specifications, tool invocation models, and runtime implementations (callable, HTTP, external). ToolManager provides a unified interface for tool lookup and invocation based on declarative runtime settings.

Resources (file, URI, external service) are also governed through policy and accessed through this subsystem.

Tools do not bypass policy, logging, or memory governance; all invocations must go through the Kernel.
"""
