from langgraph.graph import StateGraph

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.custom_agents import VectorDBAgent, MaximoAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo = MaximoAgent()
    vector_db = VectorDBAgent()

    # Define the nodes of the graph
    graph.add_node("router", supervisor.supervisor_router)
    graph.add_node("maximo_agent", maximo.perform_maximo_operation)
    graph.add_node("vector_db_agent", vector_db.handle_input)
    graph.add_node("supervisor_evaluation", supervisor.supervisor_evaluation)

    # Sepcify the edges of the graph
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", supervisor.supervisor_router, {'maximo': "maximo_agent", 'vector_db': "vector_db_agent"})
    graph.add_edge("maximo_agent", "supervisor_evaluation")
    graph.add_edge("vector_db_agent", "supervisor_evaluation")
    graph.set_finish_point("supervisor_evaluation")
    
    # Return the Compiled the graph
    return graph.compile()
