from langgraph.graph import StateGraph

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.custom_agents import VectorDBAgent, MaximoAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo = MaximoAgent()

    graph.add_node("router", supervisor.supervisor_router)

    graph.add_node("maximo_payload_generator", maximo.generate_maximo_payload)
    graph.add_node("maximo_request", maximo.perform_maximo_operation)

    graph.add_node("supervisor_evaluation", supervisor.supervisor_evaluation)

    graph.add_edge("router", "maximo_payload_generator")
    graph.add_edge("maximo_payload_generator", "maximo_request")
    graph.add_edge("maximo_request", "supervisor_evaluation")


    graph.set_entry_point("router")
    graph.set_finish_point("supervisor_evaluation")

    return graph.compile()
