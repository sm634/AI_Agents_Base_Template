from src.build_graph import build_graph
from agents.base_agent import AgentState


if __name__ == "__main__":
    
    graph = build_graph()

    with open("graph_output.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    result = graph.invoke({
            "user_input": "What is the status, description and priority of work order number 5012?"
        },
    )
    print("Final state:")
    print(result)
    
    breakpoint()
