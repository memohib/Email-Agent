from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Literal


@dataclass
class ValidationResult:
    status: Literal["approved", "rejected", "downgraded"]
    final_decision: Dict[str, Any]
    violations: List[str]
    notes: Optional[str] = None
