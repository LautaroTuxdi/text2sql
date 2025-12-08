import sqlite3
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

# Initialize Search Tool
# We wrap it to ensure it's compatible and to have control if needed
tavily_tool = TavilySearchResults(max_results=3)

@tool
def run_sql_query(query: str) -> str:
    """
    Executes a SQLite query on the 'retail.db' database and returns the results.
    """
    print(f"DEBUG: Executing SQL: {query}")
    try:
        # Clean up markdown if present
        query = query.replace("```sql", "").replace("```", "").strip()
        
        conn = sqlite3.connect('retail.db')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "NO_DATA_FOUND"
        
        return str(results)
    except sqlite3.Error as e:
        return f"SQL Error: {str(e)}"

@tool
def get_db_schema() -> str:
    """
    Returns the schema of the 'retail.db' SQLite database.
    Use this to understand the table structure before writing queries.
    """
    print("DEBUG: get_db_schema called")
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
