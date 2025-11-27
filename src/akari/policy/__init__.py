"""
Policy and governance subsystem.

This package defines the data models for policy rules, policy sets, and policy conditions, along with the PolicyEngine that evaluates whether a requested action (model.invoke, tool.invoke, memory.read, memory.write, resource.access, etc.) is authorised.

The policy system is fail-closed: if no rule matches, the action is denied.

The Kernel coordinates policy checks before any execution or memory write occurs.
"""
