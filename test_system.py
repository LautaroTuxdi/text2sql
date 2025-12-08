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
        final_state = None
        for event in app.stream(initial_state):
            print(f"DEBUG: Event keys: {event.keys()}")
            for key, value in event.items():
                if key != "__end__":
                    final_state = value
                    print(f"DEBUG: Updated final_state from key: {key}")
        
        print(f"DEBUG: Final State type: {type(final_state)}")
        # print(f"DEBUG: Final State: {final_state}")
        
        if isinstance(final_state, dict) and 'messages' in final_state and final_state['messages']:
            final_answer = final_state['messages'][-1]
        else:
            print(f"❌ Test Failed: No messages in final state. State: {final_state}")
            return

        print(f"Final Answer: {final_answer.content}")
        
        # Basic validation
        final_str = str(final_answer).lower()
        
        if expected_type == "SQL":
            # We look for evidence of DB access or SQL generation
            if "database" in final_str or "sql" in final_str or "count" in final_str or "price" in final_str:
                 print("✅ Test Passed: SQL path used (inferred from answer)")
            else:
                 print(f"⚠️ Test Warning: Expected SQL path. Answer: {final_answer}")
                 
        elif expected_type == "WEB":
            # We look for evidence of web search (trends, links, or specific fallback text)
            if "trend" in final_str or "http" in final_str or "search" in final_str or "stock" in final_str:
                print("✅ Test Passed: Web search used (inferred from answer)")
            else:
                print(f"⚠️ Test Warning: Expected Web path. Answer: {final_answer}")
                
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
