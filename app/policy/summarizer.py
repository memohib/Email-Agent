from typing import Dict, Any
from app.policy.models import CompiledPolicy


class PolicySummarizer:
    """
    Deterministically projects CompiledPolicy into
    an LLM-safe constraint object.
    """

    def summarize(self, policy: CompiledPolicy) -> Dict[str, Any]:
        return {
            "domain": policy.domain,
            "policy_version": policy.version,

            "allowed_categories": list(policy.categories.keys()),
            "urgency_levels": policy.urgency_levels,
            "risk_levels": policy.risk_levels,

            "category_decision_map": self._category_decision_map(policy),
            "decision_action_map": self._decision_action_map(policy),

            "decision_confirmation_map": self._decision_confirmation_map(policy),

            "global_rules": policy.global_rules,

            "default_fallback_decision": policy.default_fallback_decision
        }

    def _category_decision_map(self, policy: CompiledPolicy) -> Dict[str, list]:
        """
        category -> allowed decisions
        """
        return {
            category: cfg["allowed_decisions"]
            for category, cfg in policy.categories.items()
        }

    def _decision_action_map(self, policy: CompiledPolicy) -> Dict[str, list]:
        """
        decision -> allowed action types
        """
        return {
            decision: cfg.get("allowed_actions", [])
            for decision, cfg in policy.decisions.items()
        }

    def _decision_confirmation_map(self, policy: CompiledPolicy) -> Dict[str, bool]:
        """
        decision -> requires_confirmation
        """
        return {
            decision: cfg.get("requires_confirmation", False)
            for decision, cfg in policy.decisions.items()
        }
