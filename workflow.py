from langgraph.graph import StateGraph, END, START
from state import AgentState
from nodes import (
    router_node,
    sql_agent_graph,
    web_agent_graph
)

# --- Conditional Edges ---

def route_from_router(state: AgentState):
    """
    Decides where to route based on the Router's decision.
    """
    messages = state['messages']
    last_message = messages[-1].content
    
    if "DATABASE" in last_message:
        return "sql_agent"
    else:
        return "web_agent"

def route_from_sql(state: AgentState):
    """
    Decides what to do after the SQL agent finishes.
    Implements the Agentic Fallback: If NO_DATA_FOUND, go to Web.
    """
    messages = state['messages']
    last_message = messages[-1]
    print(f"DEBUG: Last message from SQL Agent: {last_message.content}")
    
    if "NO_DATA_FOUND" in last_message.content:
        return "web_agent"
    else:
        return END

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add Nodes
# We mount the compiled subgraphs directly as nodes
workflow.add_node("router", router_node)
workflow.add_node("sql_agent", sql_agent_graph)
workflow.add_node("web_agent", web_agent_graph)

# Add Edges
workflow.add_edge(START, "router")

# Conditional Edge from Router
workflow.add_conditional_edges(
    "router",
    route_from_router,
    {
        "sql_agent": "sql_agent",
        "web_agent": "web_agent"
    }
)

# Conditional Edge from SQL Agent (Fallback Logic)
workflow.add_conditional_edges(
    "sql_agent",
    route_from_sql,
    {
        "web_agent": "web_agent",
        "end": END
    }
)

# Edge from Web Agent to END
workflow.add_edge("web_agent", END)

# Compile the graph
app = workflow.compile()
