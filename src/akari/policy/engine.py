"""Simple fail-closed PolicyEngine for AKARI."""

from __future__ import annotations

from typing import Any, Dict, Optional

from akari.observability.logging import LogEvent, LogStore

from .models import PolicyDecision, PolicyEffect, PolicyRule, PolicySet


class PolicyEngine:
    """
    Evaluate policy rules for authorisation decisions.

    Deny-by-default:
    - If no rule matches, the result is DENY.
    - If a matching rule's conditions fail, that rule is skipped.
    """

    def __init__(
        self,
        policy_set: Optional[PolicySet] = None,
        log_store: LogStore | None = None,
    ) -> None:
        self._policy_set = policy_set or PolicySet(name="default")
        self._log_store = log_store


    @property
    def policy_set(self) -> PolicySet:
        return self._policy_set

    def evaluate(
        self,
        subject: str,
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        """Evaluate a policy decision for the given request."""
        context = context or {}
        ps = self._policy_set

        self._log_event(
            event_type="policy.checked",
            subject=subject,
            action=action,
            resource=resource,
            context=context,
        )

        for rule in ps.rules:
            if not self._subject_matches(rule.subject_match, subject):
                continue
            if rule.action != action:
                continue
            if not self._resource_matches(rule.resource_match, resource):
                continue

            # Check conditions (if any).
            if not self._conditions_pass(rule, context):
                continue

            # First matching rule wins.
            if rule.effect is PolicyEffect.ALLOW:
                self._log_event(
                    event_type="policy.allowed",
                    subject=subject,
                    action=action,
                    resource=resource,
                    context=context,
                    rule_id=rule.id,
                )
                return PolicyDecision(
                    allowed=True,
                    reason=f'Allowed by rule {rule.id}',
                    rule_id=rule.id,
                    policy_version=ps.version,
                )
            else:
                self._log_event(
                    event_type="policy.denied",
                    subject=subject,
                    action=action,
                    resource=resource,
                    context=context,
                    rule_id=rule.id,
                )
                return PolicyDecision(
                    allowed=False,
                    reason=f'Denied by rule {rule.id}',
                    rule_id=rule.id,
                    policy_version=ps.version,
                )

        self._log_event(
            event_type="policy.denied",
            subject=subject,
            action=action,
            resource=resource,
            context=context,
            rule_id=None,
        )
        # Fail-closed: no rule matched.
        return PolicyDecision(
            allowed=False,
            reason='No matching rule (fail-closed)',
            rule_id=None,
            policy_version=ps.version,
        )

    # ---- Matching helpers -----------------------------------------------

    @staticmethod
    def _subject_matches(pattern: str, subject: str) -> bool:
        """Match subject with simple wildcard support."""
        if pattern == '*':
            return True
        return pattern == subject

    @staticmethod
    def _resource_matches(pattern: str, resource: str) -> bool:
        """Match resource id with simple wildcard/prefix logic.

        Supported patterns:
        - "*"           : match everything.
        - "prefix*"     : match any resource starting with "prefix".
        - exact string  : match exactly.
        """
        if pattern == '*':
            return True

        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return resource.startswith(prefix)

        return pattern == resource

    @staticmethod
    def _conditions_pass(rule: PolicyRule, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions; all must pass if present."""
        for cond in rule.conditions:
            if not cond.predicate(context):
                return False
        return True

    def _log_event(
        self,
        event_type: str,
        subject: str,
        action: str,
        resource: str,
        context: Dict[str, Any],
        rule_id: Optional[str] = None,
    ) -> None:
        if self._log_store is None:
            return
        payload = {
            "action": action,
            "resource": resource,
            "context": context,
        }
        if rule_id is not None:
            payload["rule_id"] = rule_id
        event = LogEvent.new(
            event_type=event_type,
            payload=payload,
            subject=subject,
            workspace=context.get("workspace"),
            spec_id=context.get("spec_id"),
            task_id=context.get("task_id"),
        )
        self._log_store.append(event)
