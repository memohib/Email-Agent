import sys  
sys.path.append(".")

from app.agents.prompts import DECISION_AGENT_PROMPT


class DecisionAgent:
    def __init__(self, llm):
        self.llm = llm

    def decide(self, policy_summary, email, context):
        messages = [
            {"role": "system", "content": DECISION_AGENT_PROMPT},
            {"role": "user", "content": f"Policy summary: {policy_summary}"},
            {"role": "user", "content": f"Email: {email}"},
            {"role": "user", "content": f"Context: {context}"},
        ]
        result =  self.llm.invoke(
            input = messages,
        )
        return result.content

if __name__ == "__main__":
    from app.api.ai_service_tool import get_llm
    llm = get_llm()
    agent = DecisionAgent(llm=llm)
    policy_summary = ""
    email = ""
    context = ""
    decision = agent.decide(policy_summary, email, context)
    print(decision)
