from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.maximo_agent import MaximoAgent
from agents.vector_db_agent import ChromaAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo = MaximoAgent()
    vector_db = ChromaAgent()

    # Add nodes to the graph
    graph.add_node("supervisor", supervisor.handle_input)
    graph.add_node("maximo_agent", maximo.handle_input)
    graph.add_node("vector_db_agent", vector_db.handle_input)

    graph.add_conditional_edges(
        "supervisor",
        supervisor.router, 
        {"maximo": "maximo_agent","vector_db": "vector_db_agent", END: END}
    )
    graph.add_edge("maximo_agent", "supervisor")
    graph.add_edge("vector_db_agent", "supervisor")


    graph.set_entry_point("supervisor")
    graph.set_finish_point("supervisor")

    return graph.compile()
