from typing import Dict, Any, List
from app.validator.result import ValidationResult
from app.validator.exceptions import DecisionValidationError
from app.validator.rules import (
    check_risk_urgency_coherence,
    decision_allowed_for_category,
    decision_requires_confirmation,
    actions_allowed_for_decision
)


class DecisionValidator:
    """
    Deterministic validator enforcing:
    - Decision Schema v1
    - CompiledPolicy constraints
    """

    def validate(
        self,
        decision_output: Dict[str, Any],
        policy
    ) -> ValidationResult:

        violations: List[str] = []

        # Convert Pydantic object to dict if necessary
        if not isinstance(decision_output, dict):
            # Try Pydantic v2
            if hasattr(decision_output, "model_dump"):
                decision_output = decision_output.model_dump()
            # Try Pydantic v1
            elif hasattr(decision_output, "dict"):
                decision_output = decision_output.dict()

        # ─────────────────────────────
        # Layer 1: Schema Integrity
        # ─────────────────────────────
        required_fields = [
            "schema_version",
            "domain",
            "intent",
            "category",
            "urgency",
            "risk_level",
            "decision",
            "proposed_actions",
            "needs_confirmation",
            "confidence",
            "reasoning_summary"
        ]

        for field in required_fields:
            if field not in decision_output:
                raise DecisionValidationError(f"Missing required field: {field}")

        if decision_output["schema_version"] != "v1":
            raise DecisionValidationError("Unsupported schema version")

        # ─────────────────────────────
        # Layer 2: Domain & Category
        # ─────────────────────────────
        if decision_output["domain"] != policy.domain:
            violations.append("DOMAIN_MISMATCH")

        category = decision_output["category"]
        decision = decision_output["decision"]

        if category not in policy.categories:
            violations.append("UNKNOWN_CATEGORY")

        elif not decision_allowed_for_category(category, decision, policy.categories):
            violations.append("DECISION_NOT_ALLOWED_FOR_CATEGORY")

        # ─────────────────────────────
        # Layer 3: Risk & Urgency Coherence
        # ─────────────────────────────
        risk = decision_output["risk_level"]
        urgency = decision_output["urgency"]

        if not check_risk_urgency_coherence(
            risk, urgency, policy.risk_urgency_matrix
        ):
            violations.append("RISK_URGENCY_MISMATCH")

        # ─────────────────────────────
        # Layer 4: Action Safety
        # ─────────────────────────────
        action_types = [
            a["action_type"] for a in decision_output["proposed_actions"]
        ]

        if not actions_allowed_for_decision(
            decision, action_types, policy.decisions
        ):
            violations.append("ACTION_NOT_ALLOWED_FOR_DECISION")

        # Global external confirmation rule
        if (
            policy.global_rules.get("external_communication_requires_confirmation")
            and decision_requires_confirmation(decision, policy.decisions)
            and not decision_output["needs_confirmation"]
        ):
            violations.append("CONFIRMATION_REQUIRED")

        # ─────────────────────────────
        # Layer 5: Reasoning Quality
        # ─────────────────────────────
        if len(decision_output["reasoning_summary"].strip()) < 20:
            violations.append("WEAK_REASONING")

        # ─────────────────────────────
        # Resolution
        # ─────────────────────────────
        if not violations:
            # Preserve action field if present
            final_dec = dict(decision_output)
            if "action" in decision_output:
                final_dec["action"] = decision_output["action"]
            
            return ValidationResult(
                status="approved",
                final_decision=final_dec,
                violations=[]
            )

        # Hard failures
        hard_failures = {
            "DOMAIN_MISMATCH",
            "UNKNOWN_CATEGORY",
            "DECISION_NOT_ALLOWED_FOR_CATEGORY",
            "ACTION_NOT_ALLOWED_FOR_DECISION"
        }

        if any(v in hard_failures for v in violations):
            return ValidationResult(
                status="rejected",
                final_decision=self._fallback(policy),
                violations=violations,
                notes="Validator rejected unsafe or invalid decision"
            )

        # Soft failures → downgrade
        downgraded = self._downgrade(decision_output, policy)

        return ValidationResult(
            status="downgraded",
            final_decision=downgraded,
            violations=violations,
            notes="Decision downgraded due to policy safety rules"
        )

    # ─────────────────────────────
    # Fallbacks
    # ─────────────────────────────
    def _fallback(self, policy) -> Dict[str, Any]:
        return {
            "schema_version": "v1",
            "domain": policy.domain,
            "intent": "Manual review required",
            "category": "internal",
            "urgency": "can_wait",
            "risk_level": "low",
            "decision": policy.default_fallback_decision,
            "proposed_actions": [],
            "needs_confirmation": False,
            "confidence": 0.0,
            "reasoning_summary": "Validator blocked the original decision due to policy violations.",
            "action": None  # No action for fallback
        }

    def _downgrade(self, decision_output: Dict[str, Any], policy) -> Dict[str, Any]:
        downgraded = dict(decision_output)
        downgraded["decision"] = "draft_reply"
        downgraded["needs_confirmation"] = True
        downgraded["confidence"] = min(decision_output["confidence"], 0.5)
        downgraded["reasoning_summary"] += " (Decision downgraded by validator.)"
        
        # Preserve action field if present
        if "action" in decision_output:
            downgraded["action"] = decision_output["action"]
        
        return downgraded
