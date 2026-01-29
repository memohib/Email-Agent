from typing import TypedDict, Dict, Any
from app.policy.models import CompiledPolicy
from app.validator.result import ValidationResult


class GraphState(TypedDict):
    email: Dict[str, Any]
    domain: str

    context: Dict[str, Any]

    policy: CompiledPolicy
    policy_summary: Dict[str, Any]

    semantic_decision: Dict[str, Any]     
    decision_output: Any

    validation_result: ValidationResult

    final_decision: Dict[str, Any]
