from langgraph.graph import StateGraph, END

from agents.base_agent import AgentState
from agents.postgres_agent import PostGresAgent
from agents.supervisor import  SupervisorAgent
from agents.vector_db_agent import VectorDbAgent
from agents.r_general_agent import GeneralAgent
from agents.report_generator_agent import ReportGeneratorAgent


# ----- Build LangGraph -----
def build_supervisor_graph():
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent()
    post_gres_agent = PostGresAgent()
    vector_db_agent = VectorDbAgent()
    report_generator_agent = ReportGeneratorAgent()

    # Add agent and tools to the graph as nodes.
    # Add the supervisor agent to the graph
    graph.add_node(supervisor.name, supervisor.handle_input)

    # postgres agent tools
    graph.add_node("pg_generate_sql_query", post_gres_agent.generate_sql_query)
    graph.add_node("rg_generate_sql_query", post_gres_agent.generate_sql_query)
    graph.add_node("run_sql_query", post_gres_agent.run_sql_query)

    # vector db agent tools
    graph.add_node("vector_search", vector_db_agent.vector_search)

    # report generator agent tools
    graph.add_node("generate_report", report_generator_agent.generate_report)

    # handle response node
    graph.add_node("handle_response", supervisor.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        supervisor.name,
        supervisor.router, 
        {
            post_gres_agent.name: "pg_generate_sql_query", 
            vector_db_agent.name: "vector_search",
            report_generator_agent.name: "rg_generate_sql_query",
            "handle_response": "handle_response"
        }
    )

    # add edges for sub tasks.
    graph.add_edge("pg_generate_sql_query", "run_sql_query")
    graph.add_edge("rg_generate_sql_query", "generate_report")

    graph.add_edge("run_sql_query", "handle_response")
    graph.add_edge("vector_search", "handle_response")
    graph.add_edge("generate_report", "handle_response")

    # set entry and finish points
    graph.set_entry_point(supervisor.name)
    graph.set_finish_point("handle_response")

    return graph.compile()


def build_general_agent_graph():
    graph = StateGraph(AgentState)

    agent = GeneralAgent()

    # Add agent to the graph
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("generate_sql_query", agent.generate_sql_query)
    graph.add_node("vector_search", agent.vector_search)
    graph.add_node("run_query", agent.run_sql_query)
    graph.add_node("handle_response", agent.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        agent.name,
        agent.router,
        {
            "generate_sql_query": "generate_sql_query",
            "vector_search": "vector_search",
            "handle_response": "handle_response",
            END: END
        }
    )
    # add edges
    graph.add_edge("generate_sql_query", "run_query")
    graph.add_edge("vector_search", "handle_response")
    graph.add_edge("run_query", "handle_response")
    
    # set entry and finish points
    graph.set_entry_point(agent.name)
    graph.set_finish_point(agent.name)

    return graph.compile()


def build_general_agent_graph_with_report():
    graph = StateGraph(AgentState)

    agent = GeneralAgent()

    # Add nodes to  the graph
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("generate_sql_query", agent.generate_sql_query)
    graph.add_node("vector_search", agent.vector_search)
    graph.add_node("run_query", agent.run_sql_query)
    graph.add_node("generate_report", agent.generate_report)
    graph.add_node("handle_response", agent.handle_output)

    # add edges and conditional edges (requires a router function that does not return the state)
    graph.add_conditional_edges(
        agent.name,
        agent.router,
        {
            "generate_sql_query": "generate_sql_query",
            "vector_search": "vector_search",
            END: END,
        }
    )

    # add edges for sub tasks with postgres queries and report generation.
    graph.add_conditional_edges(
        "generate_sql_query", 
        agent.router_2,
        {
            "run_query": "run_query",
            "generate_report": "generate_report"
        })
    
    # add edges for sub tasks with vector search.
    graph.add_edge("run_query", "handle_response")
    graph.add_edge("vector_search", "handle_response")
    graph.add_edge("generate_report", "handle_response")


    # set entry and finish points
    graph.set_entry_point(agent.name)
    graph.set_finish_point(agent.name)

    return graph.compile()