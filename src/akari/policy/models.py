"""
Core policy models for AKARI.

These data structures represent:
- individual policy rules,
- sets of rules,
- and final policy decisions.

At v0.4.0 the model is intentionally simple but expressive enough to:
- express allow/deny based on subject, action, resource,
- optionally inspect a context dictionary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class PolicyEffect(str, Enum):
    """Policy effect: allow or deny."""

    ALLOW = "allow"
    DENY = "deny"

@dataclass
class PolicyCondition:
    """Optional condition attached to a rule.

    A condition is a callable that inspects the evaluation context and
    returns True/False. At v0.4.0 we keep this very simple and rely on
    Python callables; a richer DSL can be layered on top later.
    """

    name: str
    predicate: Callable[[Dict[str, Any]], bool]
    
    
@dataclass
class PolicyRule:
    """
    Single policy rule.

    Evaluation is based on:
    - subject_match: exact id or "*" wildcard.
    - action: exact string such as "model.invoke", "tool.invoke".
    - resource_match: exact id, prefix ("model:"), or "*".
    - effect: ALLOW or DENY.
    - conditions: optional extra checks on the context.

    Rules will be evaluated in the order provided by PolicySet.
    """

    id: str
    description: str
    subject_match: str
    action: str
    resource_match: str
    effect: PolicyEffect
    conditions: List[PolicyCondition] = field(default_factory=list)
    priority: int = 0  # reserved for future use
    

@dataclass
class PolicySet:
    """Collection of policy rules."""

    name: str
    rules: List[PolicyRule] = field(default_factory=list)
    version: Optional[str] = None
    
    
@dataclass
class PolicyDecision:
    """Result of evaluating a policy against a request."""

    allowed: bool
    reason: str
    rule_id: Optional[str] = None
    policy_version: Optional[str] = None