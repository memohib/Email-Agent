import json
from app.agents.prompts import REASONING_AGENT_PROMPT


class ReasoningAgent:
    """
    Produces a semantic (loosely structured) decision.
    """

    def __init__(self, llm):
        self.llm = llm

    def reason(self, policy_summary, email, context):
        message = [
            {"role": "system", "content": REASONING_AGENT_PROMPT},
            {"role": "user", "content": json.dumps({
                "policy": policy_summary,
                "email": email,
                "context": context,
            })}
        ]
        raw = self.llm.invoke(
            input=message,
        )

        return json.loads(raw.content)
