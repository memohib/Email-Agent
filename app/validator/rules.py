def check_risk_urgency_coherence(risk: str, urgency: str, matrix: dict) -> bool:
    allowed = matrix.get(risk, {}).get("allowed_urgency", [])
    return urgency in allowed


def decision_allowed_for_category(category: str, decision: str, categories: dict) -> bool:
    return decision in categories.get(category, {}).get("allowed_decisions", [])


def decision_requires_confirmation(decision: str, decisions: dict) -> bool:
    return decisions.get(decision, {}).get("requires_confirmation", False)


def actions_allowed_for_decision(decision: str, actions: list, decisions: dict) -> bool:
    allowed = set(decisions.get(decision, {}).get("allowed_actions", []))
    return all(a in allowed for a in actions)
