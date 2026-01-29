from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class AutonomyPolicy:
    level: str  # manual_only | semi_auto | full_auto

    
@dataclass(frozen=True)
class CompiledPolicy:
    domain: str
    version: str
    autonomy: AutonomyPolicy

    categories: Dict[str, Any]
    decisions: Dict[str, Any]
    actions: Dict[str, Any]

    risk_levels: List[str]
    urgency_levels: List[str]
    risk_urgency_matrix: Dict[str, Any]
    risk_constraints: Dict[str, Any]

    global_rules: Dict[str, Any]
    default_fallback_decision: str
