from app.policy.summarizer import PolicySummarizer
from app.validator.validator import DecisionValidator
from app.graph.state import GraphState
from app.policy.loader import PolicyLoader
from app.policy.compiler import PolicyCompiler
from app.agents.decision_agent import DecisionAgent
from app.api.ai_service_tool import get_llm, get_structured_llm
from app.agents.schema_agent import SchemaAgent
from app.agents.reasoning_agent import ReasoningAgent
from langgraph.types import interrupt, Command, RetryPolicy
from datetime import datetime, timezone
import json
import hashlib

def structure_node(state):
    schema_agent = SchemaAgent(get_structured_llm())
    decision = schema_agent.structure(
        semantic_decision=state["semantic_decision"],
        policy_summary=state["policy_summary"],
        email=state["email"],
        context=state["context"],
    )

    proposed_actions = getattr(decision, "proposed_actions", None)

    if not proposed_actions:
        # Explicit no-op (important for determinism)
        decision.action = None
    else:
        # Your system currently assumes ONE primary action
        primary = proposed_actions[0]

        action_type = primary.action_type
        if not action_type:
            raise ValueError("proposed_action missing 'action_type'")

        decision.action = action_type

    return {"decision_output": decision}


def ingest_email(state: GraphState):
    return {
        "email": state["email"],
        "domain": state.get("domain", "founder_inbox")
    }


def enrich_context(state: GraphState):
    email = state["email"]
    return {
        "context": {
            "sender": email.get("from"),
            "subject": email.get("subject"),
            "thread_id": email.get("thread_id"),
        }
    }


def load_policy(state: GraphState):
    loader = PolicyLoader()
    compiler = PolicyCompiler()
    policy = compiler.compile(loader.load_domain_policy(state["domain"]))
    return {"policy": policy}


def summarize_policy(state: GraphState):
    summary = PolicySummarizer().summarize(state["policy"])
    return {"policy_summary": summary}


def validate_decision(state: GraphState):
    validator = DecisionValidator()
    result = validator.validate(state["decision_output"], state["policy"])    
    return {"validation_result": result}


def confirmation_gate(state):
    """
    Decides whether human confirmation is required
    before execution.
    """

    validation = state["validation_result"]
    decision = validation.final_decision
    policy = state["policy"]

    # 1. Hard rejection
    if validation.status == "rejected":
        return {"route": "fallback"}

    # 2. Policy-level mandatory confirmation
    if policy.autonomy.level == "manual_only":
        return {"route": "confirm"}

    # 3. Decision-level confirmation
    if decision.get("needs_confirmation"):
        return {"route": "confirm"}

    # 4. Safe to execute
    return {"route": "execute"}


def human_confirmation(state):
    """
    Placeholder for human-in-the-loop confirmation.
    For now, we do NOT auto-approve.
    """
    decision = state["validation_result"].final_decision

    pending = decision.copy() if isinstance(decision, dict) else decision.dict()
    pending["status"] = "pending_human_confirmation"

    return {"final_decision": pending}

def execute_action(state):
    """
    Executes the action using MCP (Model Context Protocol).
    Reads action from final_decision, maps to MCP tool, and invokes.
    """
    decision = state["final_decision"]
    policy = state["policy"]
    
    # Extract the action to execute
    action = decision.get("action")
    
    if not action:
        # No action to execute
        return {
            "final_decision": {
                **decision,
                "execution_result": {
                    "status": "skipped",
                    "message": "No action specified",
                    "executed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    
    # Get MCP configuration from policy
    action_config = policy.actions.get(action)
    
    if not action_config:
        return {
            "final_decision": {
                **decision,
                "execution_result": {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "executed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    
    mcp_config = action_config.get("mcp")
    
    if not mcp_config:
        # Internal action, no MCP execution needed
        return {
            "final_decision": {
                **decision,
                "execution_result": {
                    "status": "executed",
                    "mode": "internal",
                    "message": f"Internal action '{action}' completed",
                    "executed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    
    # Extract MCP tool and arguments mapping
    tool_name = mcp_config.get("tool")
    args_mapping = mcp_config.get("args_mapping", {})
    
    # Build arguments by resolving dot-notation paths
    mcp_args = {}
    for arg_name, path in args_mapping.items():
        value = _resolve_path(state, path)
        if value is not None:
            mcp_args[arg_name] = value
    
    # Invoke MCP tool
    try:
        result = _invoke_mcp_tool(tool_name, mcp_args)
        
        return {
            "final_decision": {
                **decision,
                "execution_result": {
                    "status": "executed",
                    "mode": "mcp",
                    "tool": tool_name,
                    "arguments": mcp_args,
                    "result": result,
                    "executed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    except Exception as e:
        return {
            "final_decision": {
                **decision,
                "execution_result": {
                    "status": "error",
                    "mode": "mcp",
                    "tool": tool_name,
                    "arguments": mcp_args,
                    "error": str(e),
                    "executed_at": datetime.now(timezone.utc).isoformat()
                }
            }
        }


def _resolve_path(state, path: str):
    """
    Resolves a dot-notation path like 'email.thread_id' or 'final_decision.email_body'
    from the state.
    """
    parts = path.split(".")
    current = state
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        
        if current is None:
            return None
    
    return current


def _invoke_mcp_tool(tool_name: str, args: dict):
    """
    Invokes an MCP tool by connecting to the appropriate MCP server.
    Uses proper MCP client-server architecture via stdio protocol.
    """
    # Parse tool name (format: "service.method")
    if "." not in tool_name:
        raise ValueError(f"Invalid tool name format: {tool_name}")
    
    service, method = tool_name.split(".", 1)
    
    # Import MCP client and 
    # config
    from app.mcp import MCPClient, get_server_path
    
    # Get server path for the service
    try:
        server_path = get_server_path(service)
    except (ValueError, FileNotFoundError) as e:
        raise ValueError(f"MCP server not found for service '{service}': {e}")
    
    # Run async MCP invocation
    return asyncio.run(_async_invoke_mcp_tool(server_path, tool_name, args))


async def _async_invoke_mcp_tool(server_path: str, tool_name: str, args: dict):
    """
    Async helper to invoke MCP tool through client-server connection.
    """
    client = MCPClient()
    
    try:
        # Connect to MCP server
        await client.connect(server_path)
        
        # Call the tool
        result = await client.call_tool(tool_name, args)
        
        # Extract content from MCP result
        if hasattr(result, 'content'):
            return result.content
        return result
        
    finally:
        # Always disconnect
        await client.disconnect()


def safe_fallback(state):
    """
    Final node for rejected decisions.
    """
    return {
        "final_decision": state["validation_result"].final_decision
    }

def reasoning_node(state: GraphState):
    agent = ReasoningAgent(llm=get_llm())

    semantic = agent.reason(
        policy_summary=state["policy_summary"],
        email=state["email"],
        context=state["context"],
    )

    return {"semantic_decision": semantic}


def _hash_snapshot(snapshot: dict) -> str:
    canonical = json.dumps(snapshot, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def compose_reply_content(state: GraphState):
    """
    Generates a draft reply 
    """

    decision = state["validation_result"].final_decision

    actions = decision.get("proposed_actions", [])
    action_types = [action["action_type"] for action in actions]

    # Only compose if compose_email action is present
    if "compose_email" not in action_types:
        return state
    
    # Skip if already composed (e.g., on resume)
    if decision.get("email_body"):
        return state

    email = state["email"]

    # Call LLM and extract text content from AIMessage
    llm_response = get_llm().invoke(
        f"Compose a reply to the following email: {email} using the following context: {state['context']} and policy summary: {state['policy_summary']}"
    )
    
    # Extract just the text content from the AIMessage
    reply_body = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
    
    return {
        **state,
        "final_decision": {
            **decision,
            "email_body": reply_body
        }
    }

        
    

def confirm_interrupt(state: GraphState) -> GraphState:
    """
    Human-in-the-loop confirmation using LangGraph interrupt().
    Aligned with GraphState, CompiledPolicy, and ValidationResult.
    """

    policy = state["policy"]
    decision = state["validation_result"].final_decision
    validation = state["validation_result"]

    # -----------------
    # Hard safety guards
    # -----------------

    # Allow both "approved" and "downgraded" statuses (both may need confirmation)
    assert validation.status in ["approved", "downgraded"], \
        f"confirm_interrupt called on invalid status: {validation.status}"

    assert decision.get("needs_confirmation") is True, \
        "confirm_interrupt called when confirmation is not required"
   
   
    # -----------------
    # Immutable snapshot (persisted, not editable)
    # -----------------
    
    decision_snapshot = {
        "policy_ref": {
            "domain": policy.domain,
            "version": policy.version,
            "autonomy": policy.autonomy.level,
        },
        "decision": {
            "decision_key": decision["decision"],
            "proposed_actions": decision.get("proposed_actions"),
            "risk_level": decision["risk_level"],
            "urgency": decision["urgency"],
            "needs_confirmation": decision["needs_confirmation"],
        },
        "validation_result": {
            "status": validation.status,
            "final_decision": getattr(validation, "final_decision", None),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    decision_snapshot['decision_hash'] = _hash_snapshot(decision_snapshot)
    
    # -----------------
    # Interrupt
    # -----------------

    interrupt_payload = {
        "type": "human_confirmation_required",

       "public_context": {
            "email_subject": state["email"].get("subject"),
            "email_from": state["email"].get("from"),
            "decision": decision["decision"],
            "reasoning_summary": decision.get("reasoning_summary"),
            "risk_level": decision["risk_level"],
            "urgency": decision["urgency"],
            "confidence": decision.get("confidence"),
        },
        "decision_snapshot": decision_snapshot,

        "resume_contract": {
            "approval": None,   # "approved" | "rejected"
            "comment": None
        }
    }

    # Call interrupt and capture the resume value
    resume_value = interrupt(interrupt_payload)
    
    # -----------------
    # Update state with human approval
    # -----------------
    
    # Extract human approval from resume value
    if resume_value and isinstance(resume_value, dict):
        human_approval = resume_value.get("context", {}).get("human_approval")
        if human_approval:
            # Update context with human approval
            updated_context = {**state.get("context", {}), "human_approval": human_approval}
            return {"context": updated_context}

    return state

