import os
import sys
from workflow import app
from dotenv import load_dotenv

load_dotenv()

def main():
    print("--- Agentic Text2SQL & RAG System ---")
    print("Type 'exit' or 'quit' to stop.")
    
    # Check for API Keys
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in environment variables.")
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
            # Stream the output to see the steps
            for event in app.stream(initial_state):
                for key, value in event.items():
                    print(f"Finished Node: {key}")
                    pass
            
            # Get the final result from the last state
            # Since we can't easily access the final state from the stream loop without keeping track,
            # we can just invoke it again or better, capture the final output from the stream.
            # Actually, app.invoke() is easier for getting the final state if we don't need real-time streaming of intermediate steps.
            
            final_state = app.invoke(initial_state)
            final_answer = final_state['messages'][-1]
            
            print(f"\nAgent: {final_answer}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
