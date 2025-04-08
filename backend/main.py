from src import build_graph
from agents.base_agent import AgentState

if __name__ == "__main__":

    graph = build_graph()

    input_state = AgentState(user_input="List open work orders in Maximo")
    result = graph.invoke(input_state)
    print("Final state:")
    print(result.json(indent=2))
