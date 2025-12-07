from workflow import app
from workflow import app
import sys
from dotenv import load_dotenv

load_dotenv()

def run_test(question, expected_type):
    print(f"\n--- Testing Question: '{question}' ---")
    initial_state = {
        "question": question,
        "messages": [],
        "iterations": 0
    }
    
    try:
        final_state = app.invoke(initial_state)
        final_answer = final_state['messages'][-1]
        
        print(f"Final Answer: {final_answer}")
        
        # Basic validation
        if expected_type == "SQL":
            if "Database Results" in str(final_state.get('sql_result', '')) or "Database Results" in str(final_answer):
                 print("✅ Test Passed: SQL path used (inferred)")
            elif final_state.get('sql_query'):
                 print("✅ Test Passed: SQL query generated")
            else:
                 print("⚠️ Test Warning: Expected SQL path but might have fallen back or not clear.")
                 
        elif expected_type == "WEB":
            if final_state.get('web_results'):
                print("✅ Test Passed: Web search used")
            else:
                print("⚠️ Test Warning: Expected Web path but no web results found.")
                
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    # Test 1: Database Question
    run_test("How many customers do we have?", "SQL")
    
    # Test 2: Database Question (Specific)
    run_test("What is the price of the Laptop Pro?", "SQL")
    
    # Test 3: General Question (Web Search)
    run_test("What are the latest fashion trends for 2024?", "WEB")
    
    # Test 4: Database Question -> Empty Result -> Fallback (Adaptive RAG)
    # Asking for a product that doesn't exist
    run_test("Do we have any Flux Capacitor in stock?", "WEB")
