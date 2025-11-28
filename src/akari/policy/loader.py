"""
Minimal loader for PolicySet from a Python dictionary.

At v0.4.0 this is intentionally simple. Later versions can add:
- YAML/JSON file loading,
- richer field types and validation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import PolicyEffect, PolicyRule, PolicySet


def load_policy_set_from_dict(data: Dict[str, Any]) -> PolicySet:
    """
    Create a PolicySet from a plain dictionary.

    Expected shape:
        {
            "name": "default",
            "version": "v1",
            "rules": [
                {
                    "id": "allow-all-model-invoke",
                    "description": "...",
                    "subject_match": "*",
                    "action": "model.invoke",
                    "resource_match": "model:*",
                    "effect": "allow",
                },
                ...
            ],
        }
    """
    name = data.get("name", "default")
    version = data.get("version")
    rules_data: List[Dict[str, Any]] = data.get("rules", [])

    rules: List[PolicyRule] = []
    for rd in rules_data:
        effect_str = rd.get("effect", "deny").lower()
        effect = PolicyEffect.ALLOW if effect_str == "allow" else PolicyEffect.DENY

        rule = PolicyRule(
            id=rd["id"],
            description=rd.get("description", ""),
            subject_match=rd.get("subject_match", "*"),
            action=rd["action"],
            resource_match=rd.get("resource_match", "*"),
            effect=effect,
        )
        rules.append(rule)

    return PolicySet(name=name, rules=rules, version=version)
