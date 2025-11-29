"""Tests for PolicyEngine and simple policy loading."""

from akari.policy.engine import PolicyEngine
from akari.policy.loader import load_policy_set_from_dict
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet


def test_policy_engine_allow_and_deny() -> None:
    """PolicyEngine should allow/deny based on matching rules."""
    rules = [
        PolicyRule(
            id="allow-iris-models",
            description="Allow invoking any iris model",
            subject_match="agent:planner",
            action="model.invoke",
            resource_match="model:iris*",
            effect=PolicyEffect.ALLOW,
        ),
        PolicyRule(
            id="deny-multiply-tool",
            description="Deny using multiply tool",
            subject_match="*",
            action="tool.invoke",
            resource_match="tool:multiply",
            effect=PolicyEffect.DENY,
        ),
    ]
    policy_set = PolicySet(name="test", rules=rules, version="v1")
    engine = PolicyEngine(policy_set)

    # Allowed case.
    decision = engine.evaluate(
        subject="agent:planner",
        action="model.invoke",
        resource="model:iris_sklearn",
    )
    assert decision.allowed is True
    assert decision.rule_id == "allow-iris-models"

    # Denied case.
    decision2 = engine.evaluate(
        subject="user:demo",
        action="tool.invoke",
        resource="tool:multiply",
    )
    assert decision2.allowed is False
    assert decision2.rule_id == "deny-multiply-tool"
    
    
def test_policy_engine_fail_closed_when_no_rule_matches() -> None:
    """If no rule matches, the decision must be deny."""
    engine = PolicyEngine(PolicySet(name="empty"))

    decision = engine.evaluate(
        subject="user:someone",
        action="model.invoke",
        resource="model:unknown",
    )
    assert decision.allowed is False
    assert decision.rule_id is None
    assert "No matching rule" in decision.reason
    
    

def test_policy_loader_from_dict() -> None:
    """load_policy_set_from_dict should build rules correctly."""
    data = {
        "name": "loaded",
        "version": "v1",
        "rules": [
            {
                "id": "allow-all-model-invoke",
                "description": "Allow all model invocations",
                "subject_match": "*",
                "action": "model.invoke",
                "resource_match": "model:*",
                "effect": "allow",
            }
        ],
    }

    policy_set = load_policy_set_from_dict(data)
    assert policy_set.name == "loaded"
    assert policy_set.version == "v1"
    assert len(policy_set.rules) == 1

    engine = PolicyEngine(policy_set)
    decision = engine.evaluate(
        subject="user:any",
        action="model.invoke",
        resource="model:iris_sklearn",
    )
    assert decision.allowed is True
    assert decision.rule_id == "allow-all-model-invoke"