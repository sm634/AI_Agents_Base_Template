"""
A set of custom Agents to be implemented here. They inheret from the BaseAgent.
"""

# repo specific modules and libraries
from config import Config
from agents.base_agent import BaseAgent, AgentState
from prompt_reference.supervisor_prompt import SupervisorPrompts
from utils.handle_configs import get_llm
# third party libraries
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END



class SupervisorAgent(BaseAgent):
    def __init__(self, name:str="supervisor"):
        """A supervisor agent, which is used to route or delgate user query to other agents best able to assist with the query.
        :state: pydantic.BaseModel: The state that the agent will have access to for reading and updating. It is 
        """

        super().__init__(name)

        # instantiate the parameters for supervisor agent. 
        self.supervisor_params = Config.supervisor_params
        self.llm = get_llm(self.supervisor_params)
    

    def handle_input(self, state: AgentState):

        # instantiate the prompt with the state.
        system_message = SupervisorPrompts.supervisor_prompt.format(
            state=state
        )

        message = [
            SystemMessage(content=system_message),
            HumanMessage(content=state['user_input'])
        ]

        # call the llm with the message.
        supervisor_response = self.llm.invoke(message).content

        # update the state with the supervisor response on which agent to call next.
        state['supervisor_decision'] = supervisor_response
        print(state['supervisor_decision'])

        state['memory_chain'].append({'supervisor_response': supervisor_response})


        return state

        
    @staticmethod
    def router(state: AgentState):
        """Routing based on supervisor's response"""

        decision = state['supervisor_decision']
 
        if "vector_db" in decision:
            return "vector_db_agent"
        elif "postgres" in decision:
            return "postgres_agent"
        elif 'report' in decision:
            return "report_generator_agent"
        else:  
            # if no decision is made, return END to stop the graph.
            return "handle_response"
    
    def handle_output(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = SupervisorPrompts.supervisor_response_prompt.format(state=state)
        message = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"{state['user_input']}")
        ]
        # call the llm with the message
        agent_response = self.llm.invoke(message)

        # update the state with the agent response
        state['final_response'] = agent_response.content
        state['memory_chain'].append({
            'final_response': state['final_response']
        })
        return state