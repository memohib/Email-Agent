import sys
sys.path.append(".")
from langgraph.types import RetryPolicy
from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph import nodes
from app.graph.routing import route_after_confirmation_gate
from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles 
from langgraph.checkpoint.memory import MemorySaver
def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("ingest", nodes.ingest_email)
    graph.add_node("enrich", nodes.enrich_context)
    graph.add_node("load_policy", nodes.load_policy)
    graph.add_node("summarize_policy", nodes.summarize_policy)
    graph.add_node("reason", nodes.reasoning_node)
    graph.add_node("structure", nodes.structure_node)
    graph.add_node("validate", nodes.validate_decision)
    graph.add_node("confirm_gate", nodes.confirmation_gate)
    graph.add_node("execute", nodes.execute_action)
    graph.add_node("fallback", nodes.safe_fallback)
    graph.add_node("compose", nodes.compose_reply_content)
    graph.add_node("confirm_interrupt", nodes.confirm_interrupt)

    graph.set_entry_point("ingest")

    graph.add_edge("ingest", "enrich")
    graph.add_edge("enrich", "load_policy")
    graph.add_edge("load_policy", "summarize_policy")
    graph.add_edge("summarize_policy", "reason")
    graph.add_edge("reason", "structure")
    graph.add_edge("structure", "validate")
    graph.add_edge("validate", "compose")
    graph.add_edge("compose", "confirm_gate")
    graph.add_conditional_edges(
        "confirm_gate",
        route_after_confirmation_gate,
        {
            "confirm_interrupt": "confirm_interrupt",
            "execute": "execute",
            "fallback": "fallback",
        },  
    )
    graph.add_edge("confirm_interrupt", "confirm_gate")
    graph.add_edge("execute", END)
    graph.add_edge("fallback", END)

    # graph.add_conditional_edges(
    #     "validate",
    #     route_after_validation,
    #     {
    #         "execute": "execute",
    #         "confirm": "confirm",
    #         "fallback": "fallback",
    #     },
    # )



    return graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    graph = build_graph()
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        output_file = "graph_output.png"
        with open(output_file, "wb") as f:
            f.write(png_data)
        print(f"Graph saved to {output_file}")
    except Exception as e:
        # Fallback to printing the mermaid graph if image generation fails
        print(f"Could not generate image: {e}")
        print(graph.get_graph().draw_mermaid())
