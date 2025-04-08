from agents.base_agent import AgentState
from agents.supervisor import SupervisorAgent

supervisor = SupervisorAgent()

user_input = "I want to know how to fix an order issue related to ID 619. Consult the document to help."
state = AgentState(user_input=user_input)

response = supervisor.classify_query(state=state)
print(response)

breakpoint()
