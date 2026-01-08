from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.supervisor import  SupervisorAgent
from agents.vector_db_agent import VectorDbAgent


# ----- Build LangGraph -----
def build_supervisor_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    vector_db_agent = VectorDbAgent()

    # Add agent to the graph
    graph.add_node(supervisor.name, supervisor.handle_input)
    graph.add_node(vector_db_agent.name, vector_db_agent.handle_input)
    # Add tools nodes
    graph.add_node("vector_db_tools", vector_db_agent.use_vector_db_tools)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        supervisor.name,
        supervisor.router, 
        {
            vector_db_agent.name: vector_db_agent.name, 
            supervisor.name: supervisor.name, 
            END: END
        }
    )

    graph.add_conditional_edges(
        vector_db_agent.name,
        vector_db_agent.router,
        {"vector_db_tools": "vector_db_tools", supervisor.name: supervisor.name}
    )

    graph.add_edge("vector_db_tools", vector_db_agent.name)


    graph.set_entry_point(supervisor.name)
    graph.set_finish_point(supervisor.name)

    return graph.compile()


def vector_db_agent_graph():
    graph = StateGraph(AgentState)

    agent = VectorDbAgent()

    # Add agent to the graph
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("vector_search", agent.use_vector_db_tools)
    graph.add_node("handle_response", agent.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    # graph.add_conditional_edges(
    #     agent.name,
    #     agent.router,
    #     {
    #         "vector_search": "vector_search",
    #         "handle_response": "handle_response",
    #         END: END
    #     }
    # )
    # add edges
    graph.add_edge(agent.name, "vector_search")
    graph.add_edge("vector_search", "handle_response")
    # graph.add_edge("run_query", "handle_response")
    
    # set entry and finish points
    graph.set_entry_point(agent.name)
    graph.set_finish_point(agent.name)

    return graph.compile()