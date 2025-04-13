from agents.base_agent import AgentState
from agents.supervisor import SupervisorAgent
from agents.maximo_agent import MaximoAgent


def test_supervisor_classification():
    supervisor = SupervisorAgent()

    user_input1 = "I want to know how to fix an order issue related to ID 619. Consult the document to help."
    state = AgentState(user_input=user_input1)

    response1 = supervisor.classify_query(state=state)
    assert response1 == "vector_db"

    user_input2 = "What is the status of work order 12345?"
    state = AgentState(user_input=user_input2)
    response2 = supervisor.classify_query(state=state)
    assert response2 == "maximo"


def test_generate_maximo_payload():
    import ast
    
    maximo_agent = MaximoAgent()
    user_input = "What is the status, description and priority of work order number 5012?"
    state = AgentState(user_input=user_input)

    # Simulate the classification step
    state.supervisor_decision = "maximo"

    # Perform the payload generator
    updated_state = maximo_agent.generate_maximo_payload(state=state)
    return updated_state

def test_get_maximo_wo_details():
    maximo_agent = MaximoAgent()
    user_input = "What is the status, description and priority of work order number 5012?"
    state = AgentState(user_input=user_input)

    # simulate the payload generation step.
    state = test_generate_maximo_payload()
    print(state.maximo_payload, "\n\n")

    # Simulate the classification step
    state.supervisor_decision = "maximo"

    # Perform the Maximo operation
    response = maximo_agent.get_maximo_wo_details(state=state)
    return response

def test_maximo_tool_use():
    maximo_agent = MaximoAgent()
    user_input = "What is the status, description and priority of work order number 5012?"
    # user_input = "Update the work order 5012 to priority 1."
    state = AgentState(user_input=user_input)

    # simulate the payload generation step.
    response = maximo_agent.handle_input(state=state)
    return response, state

def test_supervisor_response():
    supervisor = SupervisorAgent()
    user_input = "What is the status, description and priority of work order number 5012?"
    # user_input = "Update the work order 5012 to priority 1."
    state = AgentState(user_input=user_input)

    # simulate the supervisor response.
    supervisor_response = supervisor.handle_input(state=state)
    
    return supervisor_response
