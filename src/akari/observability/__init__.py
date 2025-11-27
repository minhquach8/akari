"""
Observability subsystem.

This package contains logging and run-tracking components, including LogEvent, LogStore (in-memory or persistent), ExperimentRun, RunTracker, and RunStore backends.

All critical behaviour—task lifecycle, policy decisions, memory access— is recorded as structured events, enabling audit, replay, and debugging.

Persistent backends (JSONL or SQLite) are introduced progressively while keeping interfaces stable.
"""
