import sqlite3
import os
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState

from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
# Using Groq as requested by the user
llm = ChatOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile", # Using latest supported Groq model
    temperature=0
)

# Initialize Search Tool
search_tool = TavilySearchResults(max_results=3)

def get_db_schema():
    conn = sqlite3.connect('retail.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema += f"Table: {table_name}\n"
        for col in columns:
            schema += f"  - {col[1]} ({col[2]})\n"
        schema += "\n"
    conn.close()
    return schema

DB_SCHEMA = get_db_schema()

# --- Nodes ---

def query_analyzer(state: AgentState):
    """
    Analyzes the user's question to decide if it requires database access or web search.
    """
    print("--- QUERY ANALYZER ---")
    question = state['question']
    
    system_prompt = """You are a query router. Your job is to classify the user's question into one of two categories:
    1. 'DATABASE': If the question relates to internal company data such as customers, products, sales, inventory, or reviews.
    2. 'GENERAL': If the question relates to general knowledge, external trends, news, or anything not in the internal database.
    
    Return ONLY the word 'DATABASE' or 'GENERAL'."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    classification = chain.invoke({"question": question}).strip().upper()
    
    return {"messages": [f"Analyzed query type: {classification}"]}

def sql_generator(state: AgentState):
    """
    Generates a SQLite compatible query based on the user question and DB schema.
    """
    print("--- SQL GENERATOR ---")
    question = state['question']
    messages = state.get('messages', [])
    
    # Check if there's an error message from the previous step (self-correction)
    last_message = messages[-1] if messages else ""
    error_context = ""
    if "SQL Error:" in str(last_message):
        error_context = f"\n\nPREVIOUS ERROR: {last_message}\nFix the SQL query based on this error."
    
    system_prompt = f"""You are an expert SQL developer. Your goal is to write a valid SQLite query to answer the user's question.
    
    Here is the Database Schema:
    {DB_SCHEMA}
    
    Rules:
    1. Return ONLY the raw SQL query. Do not use markdown formatting (like ```sql).
    2. Do not include any explanations.
    3. If the question cannot be answered with the given schema, try to find the closest match or return a query that checks for existence.
    {error_context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    sql_query = chain.invoke({"question": question}).strip()
    
    # Clean up markdown if present (just in case)
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    return {"sql_query": sql_query, "iterations": state.get("iterations", 0) + 1}

def sql_executor_validator(state: AgentState):
    """
    Executes the SQL query and validates the result.
    """
    print("--- SQL EXECUTOR ---")
    sql_query = state['sql_query']
    
    try:
        conn = sqlite3.connect('retail.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"sql_result": "EMPTY_SET", "messages": ["Query executed successfully but returned no results."]}
        
        # Format results for easier reading
        result_str = str(results)
        return {"sql_result": result_str}
        
    except sqlite3.Error as e:
        return {"sql_result": "ERROR", "messages": [f"SQL Error: {str(e)}"]}

def web_searcher(state: AgentState):
    """
    Performs a web search if the query is general or if DB lookup failed.
    """
    print("--- WEB SEARCHER ---")
    question = state['question']
    
    try:
        results = search_tool.invoke(question)
        # Format web results
        web_content = "\n".join([f"- {res['content']} (Source: {res['url']})" for res in results])
        return {"web_results": web_content}
    except Exception as e:
        return {"web_results": f"Error performing web search: {str(e)}"}

def final_synthesizer(state: AgentState):
    """
    Synthesizes the final answer using either SQL results or Web results.
    """
    print("--- FINAL SYNTHESIZER ---")
    question = state['question']
    sql_result = state.get('sql_result')
    web_results = state.get('web_results')
    
    context = ""
    if sql_result and sql_result != "ERROR" and sql_result != "EMPTY_SET":
        context = f"Database Results: {sql_result}"
    elif web_results:
        context = f"Web Search Results: {web_results}"
    else:
        context = "No relevant information found in database or web."
        
    system_prompt = """You are a helpful customer support assistant for a retail company.
    Use the provided context to answer the user's question naturally and professionally.
    If the context contains database results, summarize them clearly.
    If the context contains web search results, summarize the key findings.
    If no information is found, politely apologize and offer to help with something else.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", f"Question: {question}\n\nContext:\n{context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"question": question, "context": context})
    
    return {"messages": [answer]}
