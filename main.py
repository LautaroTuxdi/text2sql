import os
import sys
from workflow import app
from dotenv import load_dotenv

load_dotenv()

def main():
    print("--- Agentic Text2SQL & RAG System ---")
    print("Type 'exit' or 'quit' to stop.")
    
    # Check for API Keys
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("WARNING: DEEPSEEK_API_KEY not found in environment variables.")
    if not os.environ.get("TAVILY_API_KEY"):
        print("WARNING: TAVILY_API_KEY not found in environment variables.")

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            initial_state = {
                "question": user_input,
                "messages": [],
                "iterations": 0
            }
            
            print("\nProcessing...")
            final_state = app.invoke(initial_state)
            final_answer = final_state['messages'][-1]
            print(f"\nAgent: {final_answer.content}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
