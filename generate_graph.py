from workflow import app

from langchain_core.runnables.graph import MermaidDrawMethod

def generate_graph_image():
    try:
        # Get the graph object
        graph = app.get_graph(xray=True)
        
        # Save Mermaid text (Fallback)
        mermaid_txt = graph.draw_mermaid()
        with open("graph.mmd", "w") as f:
            f.write(mermaid_txt)
        print("Graph definition saved as 'graph.mmd'. You can view it at https://mermaid.live")

        # Generate the graph image
        graph_png = graph.draw_mermaid_png(
            draw_method=MermaidDrawMethod.PYPPETEER,
        )
        
        # Save to file
        with open("graph.png", "wb") as f:
            f.write(graph_png)
            
        print("Graph image saved as 'graph.png'")
    except Exception as e:
        print(f"Error generating graph image: {e}")
        print("Make sure you have graphviz installed if needed, or check LangGraph dependencies.")
        print("You can still use 'graph.mmd' to visualize the graph manually.")

if __name__ == "__main__":
    generate_graph_image()
