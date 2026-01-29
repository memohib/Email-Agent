import sys
from langgraph.checkpoint.memory import MemorySaver
sys.path.append(".")
from app.graph.dag import build_graph
from langgraph.types import Command


def format_workflow_result(result):
    """Format workflow result into human-readable output"""
    
    print("\n" + "="*80)
    print("📧 EMAIL AGENT WORKFLOW RESULT")
    print("="*80)
    
    # Email Summary
    email = result.get("email", {})
    print(f"\n📨 EMAIL DETAILS:")
    print(f"   From: {email.get('from')}")
    print(f"   Subject: {email.get('subject')}")
    print(f"   Thread ID: {email.get('thread_id')}")
    
    # AI Decision
    decision_output = result.get("decision_output")
    if decision_output:
        print(f"\n🤖 AI DECISION:")
        print(f"   Category: {decision_output.category}")
        print(f"   Decision: {decision_output.decision}")
        print(f"   Urgency: {decision_output.urgency}")
        print(f"   Risk Level: {decision_output.risk_level}")
        print(f"   Confidence: {decision_output.confidence * 100:.1f}%")
        print(f"   Needs Confirmation: {decision_output.needs_confirmation}")
    
    # Validation Result
    validation = result.get("validation_result")
    if validation:
        print(f"\n✅ VALIDATION RESULT:")
        status_icons = {
            "approved": "🟢",
            "downgraded": "🟡",
            "rejected": "🔴"
        }
        icon = status_icons.get(validation.status, "⚪")
        print(f"   Status: {icon} {validation.status.upper()}")
        
        if validation.violations:
            print(f"   ⚠️  Violations: {', '.join(validation.violations)}")
        else:
            print(f"   ✓ No violations")
            
        if validation.notes:
            print(f"   📝 Notes: {validation.notes}")
    
    # Final Decision
    final_decision = result.get("final_decision", {})
    if final_decision:
        print(f"\n🎯 FINAL DECISION:")
        print(f"   Decision: {final_decision.get('decision')}")
        print(f"   Status: {final_decision.get('status', 'N/A')}")
        print(f"   Confidence: {final_decision.get('confidence', 0) * 100:.1f}%")
        
        # Actions
        actions = final_decision.get('proposed_actions', [])
        if actions:
            print(f"   Proposed Actions:")
            for action in actions:
                print(f"      • {action.get('action_type')}: {action.get('description')}")
        
        # Reasoning
        reasoning = final_decision.get('reasoning_summary', '')
        if reasoning:
            print(f"\n💭 REASONING:")
            # Wrap reasoning text
            max_width = 70
            words = reasoning.split()
            line = "   "
            for word in words:
                if len(line) + len(word) + 1 <= max_width:
                    line += word + " "
                else:
                    print(line)
                    line = "   " + word + " "
            if line.strip():
                print(line)
    
    # Workflow Status
    print(f"\n📊 WORKFLOW STATUS:")
    if final_decision.get('status') == 'pending_human_confirmation':
        print(f"   ⏸️  PAUSED - Waiting for human confirmation")
        print(f"   Next Step: Resume workflow with approval/rejection")
    else:
        print(f"   ✓ Workflow completed")
    
    print("="*80 + "\n")


graph = build_graph()

TEST_EMAILS = {}

TEST_EMAILS["investor_follow_up"] = {
    "from": "partner@vcfirm.com",
    "to": "founder@startup.com",
    "subject": "Following up on our last discussion",
    "body": (
        "Hi Mohib,\n\n"
        "Just wanted to follow up on our last conversation regarding your fundraising plans. "
        "Let me know if you've had a chance to think about next steps.\n\n"
        "Best,\n"
        "Alex"
    ),
    "thread_id": "thread-101",
    "attachments": []
}

config = {"configurable":{"thread_id":"thread-101"}}
email_payload = TEST_EMAILS["investor_follow_up"]
## Streaming each node output

for node in graph.stream(
    input={
    "email": email_payload,
    "domain": "founder_inbox",
},
stream_mode="updates",
config = config):
    print(node)

# # Display formatted result
format_workflow_result(node)

resumed_result = graph.invoke(Command(resume={
            "context": {
                "human_approval": {
                    "approval": "approved",
                    "comment": "Looks good"
                }
            }
        }
    ), config=config)

print("\n" + "="*80)
print("🔄 RESUMED WORKFLOW AFTER HUMAN APPROVAL")
print("="*80)
print(f"Resumed result keys: {resumed_result.keys()}")
print(f"Final decision: {resumed_result.get('final_decision')}")
print("="*80 + "\n")

# Display formatted result
format_workflow_result(resumed_result)


