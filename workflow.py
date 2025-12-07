from langgraph.graph import StateGraph, END, START
from state import AgentState
from nodes import (
    query_analyzer,
    sql_generator,
    sql_executor_validator,
    web_searcher,
    final_synthesizer
)

# --- Conditional Edges ---

def route_query(state: AgentState):
    """
    Decides where to route after analysis.
    """
    # The analyzer returns a message with the classification
    last_message = state['messages'][-1]
    if "DATABASE" in last_message:
        return "sql_generator"
    else:
        return "web_searcher"

def check_sql_validity(state: AgentState):
    """
    Checks the result of the SQL execution.
    """
    sql_result = state.get('sql_result')
    iterations = state.get('iterations', 0)
    
    if sql_result == "ERROR":
        if iterations >= 3: # Prevent infinite loops
            return "web_searcher"
        return "sql_generator" # Loop back to fix
    elif sql_result == "EMPTY_SET":
        return "web_searcher" # Fallback to web
    else:
        return "final_synthesizer" # Success

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("query_analyzer", query_analyzer)
workflow.add_node("sql_generator", sql_generator)
workflow.add_node("sql_executor_validator", sql_executor_validator)
workflow.add_node("web_searcher", web_searcher)
workflow.add_node("final_synthesizer", final_synthesizer)

# Add Edges
workflow.add_edge(START, "query_analyzer")

# Conditional Edge from Analyzer
workflow.add_conditional_edges(
    "query_analyzer",
    route_query,
    {
        "sql_generator": "sql_generator",
        "web_searcher": "web_searcher"
    }
)

# Edge from Generator to Executor
workflow.add_edge("sql_generator", "sql_executor_validator")

# Conditional Edge from Executor
workflow.add_conditional_edges(
    "sql_executor_validator",
    check_sql_validity,
    {
        "sql_generator": "sql_generator",
        "web_searcher": "web_searcher",
        "final_synthesizer": "final_synthesizer"
    }
)

# Edge from Web Searcher to Synthesizer
workflow.add_edge("web_searcher", "final_synthesizer")

# Edge from Synthesizer to END
workflow.add_edge("final_synthesizer", END)

# Compile the graph
app = workflow.compile()
