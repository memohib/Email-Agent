from typing import Any, Dict
import json
from langchain_core.messages import HumanMessage
import sys
sys.path.append(".")
from app.agents.schemas import UniversalDecisionSchemaV1


class SchemaAgent:
    """
    Converts a semantic (loosely structured) decision into a
    UniversalDecisionSchemaV1 using LLM structured output.

    Guarantees:
    - All required fields exist
    - Field types are correct
    - Output is a Pydantic object

    Does NOT guarantee:
    - Policy correctness
    - Safety
    - Valid decision (validator handles that)
    """

    def __init__(self, llm):
        # Wrap the LLM with structured output
        self.structured_llm = llm.with_structured_output(
            UniversalDecisionSchemaV1,
            include_raw=True,   # important for debugging
        )

    def structure(
        self,
        semantic_decision: Dict[str, Any],
        policy_summary: Dict[str, Any],
        email: Dict[str, Any],
        context: Dict[str, Any] | None = None,
    ) -> UniversalDecisionSchemaV1:
        """
        Returns a UniversalDecisionSchemaV1 Pydantic object.
        Raises if structured parsing fails.
        """
        messages = HumanMessage(content=json.dumps({
                "semantic_decision": semantic_decision,
                "policy": policy_summary,
                "email": email,
                "context": context or {},
            }))
        
        # Invoke the structured LLM
        result = self.structured_llm.invoke( 
            [messages]
        )

        # LangChain always returns a dict when include_raw=True
        parsing_error = result.get("parsing_error")
        parsed = result.get("parsed")

        if parsing_error:
            raise ValueError(
                f"SchemaAgent failed to produce valid structured output: {parsing_error}"
            )

        if parsed is None:
            raise ValueError("SchemaAgent returned no parsed output")

        # `parsed` is already a Pydantic object
        return parsed
