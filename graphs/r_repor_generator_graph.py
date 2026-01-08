#import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import necessary modules and functions from langgraph
#from langgraph import Graph, Node, add_edge
from langgraph.graph import StateGraph
from agents.base_agent import AgentState 
from agents.report_generator_agent import ReportGeneratorAgent


def build_report_generator_graph():
    graph = StateGraph(AgentState)
    agent = ReportGeneratorAgent()

    # Define the nodes

  #  postgres_db_agent = Node("vector_db_agent")
  #  generate_sql_query = Node("generate_sql_query")
  #  run_query = Node("run_query")
    graph.add_node(agent.name, agent.handle_input)
    graph.add_node("generate_sql_query", agent.generate_sql_query)
    graph.add_node("generate_report", agent.use_tools)
    #generate_report = Node("generate_report")

    # Create the graph
    #report_generator_agent_graph = Graph("report_generator_agent_graph")

    # Add nodes to the graph
    #report_generator_agent_graph.add_node(vector_db_agent)
    #report_generator_agent_graph.add_node(generate_sql_query)
    #report_generator_agent_graph.add_node(run_query)
    #report_generator_agent_graph.add_node(generate_report)

    # Link the nodes with add_edge()
    #add_edge(report_generator_agent_graph, vector_db_agent, generate_sql_query)
    #add_edge(report_generator_agent_graph, generate_sql_query, run_query)
    #add_edge(report_generator_agent_graph, run_query, generate_report)
    graph.add_edge(agent.name, "generate_sql_query")
    graph.add_edge("generate_sql_query", "generate_report")
    # Save the graph to the graphs/ folder
    #report_generator_agent_graph.save("graphs/report_generator_agent_graph")
    graph.set_entry_point(agent.name)
    graph.set_finish_point("generate_report")

    return graph.compile()