from agents.base_agent import AgentState
from agents.vector_db_agent import VectorDbAgent
from agents.postgres_agent import PostGresAgent


def test_postgres_agent_tools():

    user_input = 'retrieve all the data in the TEST database.'
    postgres_query = 'SELECT * FROM "TEST"'
    state = AgentState(
            {
                'user_input': user_input,
                'supervisor_decision': '',
                'postgres_query': postgres_query,
                'tool_calls': '',
                'agent_tool_retries': '',
                'agent_max_tool_retries': '',
                'postgres_agent_response': '',
                'final_response': '',
                'memory_chain': []
            }
    )
    # State before update.
    print(state)

    postgres_agent = PostGresAgent()
    state = postgres_agent.handle_input(state=state)
    
    print("Updated State:\n", state)

    state = postgres_agent.use_postgres_tools(state=state)

    print("Post tool use state: \n", state)
    
    breakpoint()


def test_vectordb_agent_tools():

    user_input="which version of jboss supports open jdk 11???"
    # search=""
    state = AgentState(
            {
                'user_input': user_input,
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
            }
    )
    
    print(state)
    vector_db_agent = VectorDbAgent()

    # test tool call.
    state = vector_db_agent.vector_search(state=state)
    print("post tool use state \n", state)
    breakpoint()


def test_general_agent_tools():


    user_input = "How many records are there in the jira database?"
    state = AgentState(
            {
                'user_input': user_input,
                'supervisor_decision': '',
                'tool_calls': '',
                'agent_tool_retries':0,
                'agent_max_tool_retries': 3,
                'postgres_query': '',
                'postgres_agent_response': '',
                'vector_db_agent_response': '',
                'final_response': '',
                'memory_chain': []
            }
    )
    agent = GeneralAgent()

    state = agent.handle_input(state=state)
    print(state)
    while len(state['postgres_agent_response']) < 1:
        breakpoint()
        state = agent.use_tools(state=state)
        print("updated state", state)

    user_input = "What technologies are supported for containerized deployment of FCC application?"
 

    breakpoint()