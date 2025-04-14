from langgraph.graph import StateGraph

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.maximo_agent import MaximoAgent
from agents.milvus_agent import MilvusAgent


# ----- Build LangGraph -----
def build_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    maximo = MaximoAgent()
    milvus = MilvusAgent()

    # Add nodes to the graph
    graph.add_node("supervisor", supervisor.handle_input)
    # graph.add_node("supervisor_router", supervisor.router)
    graph.add_node("maximo_agent", maximo.handle_input)
    graph.add_node("maximo_tools", maximo.use_maximo_tools)
    graph.add_node("milvus_agent", milvus.handle_input)

    # graph.add_edge("supervisor", "supervisor_router")
    graph.add_conditional_edges(
        "supervisor", 
        supervisor.handle_input, 
        {"maximo": "maximo_agent", "milvus": "milvus_agent", "unknown": "supervisor"}
    )
    # graph.add_edge("maximo_agent", "maximo_agent_router")
    graph.add_edge(
        "maximo_agent", 
        "supervisor"
    )
    graph.add_edge("maximo_agent", "maximo_tools")
    graph.add_edge("maximo_tools", "maximo_agent")
    graph.add_edge("milvus_agent", "supervisor")


    graph.set_entry_point("supervisor")
    graph.set_finish_point("supervisor")

    return graph.compile()
