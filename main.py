import os
os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1263111'  # Use a valid revision number
from pyppeteer import launch

from dotenv import load_dotenv
_ = load_dotenv(override=True)

#from graphs.build_graph import build_general_agent_graph
from graphs.build_graph import build_supervisor_graph

def test_supervisor_agent():
    print("Building the supervisor agent graph...")
    graph = build_supervisor_graph()

    file_name = "supervisor_agent_graph.png"

    with open(file_name, "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print(f"Graph has been built and saved as {file_name}")

    print("Milvus pass: ", os.environ['milvusPass'])
    print("Milvus host: ", os.environ['grpcHost'])
    print("Milvus port: ", os.environ['grpcPort'])
    print("Milvus user ", os.environ['milvusUser'])

    thread = {"configurable": {"thread_id": "1"}}

#     # for vectordb test
#     user_input="How many records are there in the jira database?"
    query = "What technologies are supported for containerized deployment of FCC application?"

    for output in graph.stream(
            {
                'user_input': query,
                'supervisor_decision': '',
                'tool_calls': '',
                'agent_tool_retries': 0,
                'agent_max_tool_retries': 3,
                'postgres_query': '',
                'postgres_agent_response': '',
                'vector_db_agent_response': '',
                'report_generation_requested': '',
                'report_generation_response': '',
                'final_response': '',
                'memory_chain': []
            }, thread):
    
        print(output)

    breakpoint()

from langchain_core.runnables.graph import MermaidDrawMethod


def test_general_agent_with_reports():
    graph = build_general_agent_graph_with_report()

    file_name = "general_agent_with_report.png"
    with open(file_name, "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print(f"Graph has been built and saved as {file_name}")

    # queries for different tests.
    query="How many records are there in the jira database?"
    # user_input = "What technologies are supported for containerized deployment of FCC application?"
    # query = "Generate a report of the number of issues by status in the jira database."

    # result = graph.invoke(            
    #             {
    #                 'user_input': query,
    #                 'supervisor_decision': '',
    #                 'tool_calls': '',
    #                 'agent_tool_retries':0,
    #                 'agent_max_tool_retries': 3,
    #                 'postgres_query': '',
    #                 'postgres_agent_response': '',
    #                 'vector_db_agent_response': '',
    #                 'report_generation_requested': '',
    #                 'report_generation_response': '',
    #                 'final_response': '',
    #                 'memory_chain': []
    #             }
    #         )
    # print(result['final_response'])

    breakpoint()

# def test_report_generator_agent():
#     graph = build_report_generator_graph()

#     with open("report_generator_agent.png", "wb") as image_file:
#         image_file.write(graph.get_graph().draw_png())
    
#     print("Graph has been built and saved as report_generator_agent.png")
def test_report_generator_agent():
    graph = build_report_generator_graph()

    with open("report_generator_agent.png", "wb") as image_file:
    #    image_file.write(graph.get_graph().draw_png())
         graph.get_graph().draw_mermaid_png(output_file_path="graph.png", draw_method=MermaidDrawMethod.PYPPETEER) 
    print("Graph has been built and saved as report_generator_agent.png")
    
def test_vector_agent():
    graph = vector_db_agent_graph()

    with open("graph_postgres.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # for vectordb test
    # user_input="How many records are there in the jira database?"
    user_input = "Which version of JBoss supports open jdk 11?"

    result = graph.invoke(
            {
                    'user_input': user_input,
                    'supervisor_decision': '',
                    'tool_calls': '',
                    'agent_tool_retries':0,
                    'agent_max_tool_retries': 3,
                    'vector_db_agent_response': '',
                    'final_response': '',
                    'memory_chain': []
                }
        )
    print(result['final_response'])


if __name__ == "__main__":
    
    test_supervisor_agent()
