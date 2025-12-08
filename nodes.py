import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from state import AgentState
from tools import run_sql_query, get_db_schema, tavily_tool
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)

# --- Agent Factories ---

def make_sql_agent():
    """
    Creates the SQL Specialist ReAct Agent.
    """
    system_prompt = """You are a SQL Expert. 
    The database has the following tables:
    - customers (id, name, email, join_date)
    - products (id, name, price, stock)
    - sales (id, customer_id, product_id, date, quantity)
    - reviews (id, product_id, rating, comment)
    
    1. Write and execute a SQLite query using `run_sql_query` to answer the user's specific question.
    2. If the query returns "NO_DATA_FOUND", explicitly state "NO_DATA_FOUND" in your final answer.
    3. If you find data, answer the user's question directly based on the results.
    """
    return create_react_agent(llm, tools=[run_sql_query], prompt=system_prompt)

def make_web_agent():
    """
    Creates the Web Researcher ReAct Agent.
    """
    system_prompt = """You are a Researcher. 
    Use the `tavily_search_results_json` tool to find current events, trends, or general information.
    Summarize the findings for the user.
    """
    # Note: TavilySearchResults name might vary in tool calling, usually it's auto-detected
    return create_react_agent(llm, tools=[tavily_tool], prompt=system_prompt)


# --- Compiled Subgraphs ---
# We export these to be mounted in the main graph
sql_agent_graph = make_sql_agent()
web_agent_graph = make_web_agent()


# --- Nodes ---

def router_node(state: AgentState):
    """
    Analyzes the user's question to decide if it requires database access or web search.
    """
    print("--- ROUTER ---")
    question = state['question']
    
    system_prompt = """You are a query router. Classify the user's question:
    1. 'DATABASE': If it relates to internal company data (sales, products, customers, reviews, inventory).
    2. 'GENERAL': If it relates to external trends, news, or general knowledge.
    
    Return ONLY the word 'DATABASE' or 'GENERAL'."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    classification = chain.invoke({"question": question}).strip().upper()
    
    if classification == "DATABASE":
        return {"messages": [SystemMessage(content=f"ROUTER_DECISION: {classification}")]}
    
    return {"messages": [SystemMessage(content=f"ROUTER_DECISION: {classification}")]}
