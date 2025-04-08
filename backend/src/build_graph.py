from langgraph.graph import StateGraph

from agents.supervisor import  SupervisorAgent
from agents.custom_agents import VectorDBAgent, MaximoAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent(llm=llm)
    maximo = MaximoAgent(llm=llm)
    vector_db = VectorDBAgent(llm=llm)

    graph.add_node("supervisor", supervisor.run)
    graph.add_node("maximo", maximo.run)
    graph.add_node("vector_db", vector_db.run)
    graph.add_node("supervisor_postprocess", supervisor.postprocess)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", supervisor_router)
    graph.add_edge("maximo", "supervisor_postprocess")
    graph.add_edge("vector_db", "supervisor_postprocess")
    graph.set_finish_point("supervisor_postprocess")

    return graph.compile()
