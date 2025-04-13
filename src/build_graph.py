from langgraph.graph import StateGraph

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.maximo_agent import VectorDBAgent, MaximoAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo = MaximoAgent()

    graph.add_node("supervisor", supervisor.handle_input)
    graph.add_node("maximo_agent", maximo.handle_input)

    graph.add_edge("router", "maximo_payload_generator")
    graph.add_edge("maximo_payload_generator", "maximo_request")
    graph.add_edge("maximo_request", "supervisor_evaluation")


    graph.set_entry_point("router")
    graph.set_finish_point("supervisor_evaluation")

    return graph.compile()
