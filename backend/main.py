from src.build_graph import build_graph
from agents.base_agent import AgentState
from IPython.display import Image


if __name__ == "__main__":
    
    graph = build_graph()

    with open("graph_output.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())

    input_state = AgentState(user_input="What is the status, description and priority of work order number 5012?")
    result = graph.invoke(input_state)
    print("Final state:")
    print(result.json(indent=2))
