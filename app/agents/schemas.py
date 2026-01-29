from pydantic import BaseModel, Field
from typing import List, Literal

class ProposedAction(BaseModel):
    action_type: str = Field(description="Action type allowed by policy")
    description: str = Field(description="Description of the action")
    target: str = "email"

class UniversalDecisionSchemaV1(BaseModel):
    schema_version: Literal["v1"] = "v1"

    domain: str
    intent: str

    category: str
    urgency: str
    risk_level: str
    action: str

    decision: str

    proposed_actions: List[ProposedAction]

    needs_confirmation: bool
    confidence: float = Field(ge=0.0, le=1.0)

    reasoning_summary: str