"""
A set of custom Agents to be implemented here. They inheret from the BaseAgent.
"""

# native python
import os
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

        """To be implemented"""
        # instantiate the prompt with the state.
        user_input = state['user_input']
        
        # initialize the states if it does not already contain a value to be updated later.
        if 'maximo_payload' not in state:
            state.setdefault('maximo_payload', '')
        if 'maximo_agent_response' not in state:
            state.setdefault('maximo_agent_response', '')
        if 'vector_db_agent_response' not in state:
            state.setdefault('vector_db_agent_response', '')
        if 'tool_calls' not in state:
            state.setdefault('tool_calls', '')


        agent_response = str(state['maximo_agent_response']) + '\n' + str(state['vector_db_agent_response'])

        system_message = SupervisorPrompts.supervisor_prompt.format(
            user_input=user_input,
            agent_response=agent_response
        )

        message = [
            SystemMessage(content=system_message),
            HumanMessage(content=state['user_input'])
        ]

        # call the llm with the message.
        supervisor_response = self.llm.invoke(message).content

        # update the state with the supervisor response.
        state.setdefault('memory_chain', []).append({'supervisor_response': supervisor_response})

        routing_options = ['maximo', 'vector_db', 'unknown']
        if supervisor_response in routing_options:
            state.setdefault('supervisor_decision', '')
            state['supervisor_decision'] = supervisor_response

        else:
            state.setdefault('final_response', '')
            state['final_response'] = supervisor_response

        return state

        
    @staticmethod
    def router(state: AgentState):

        decision = state.get('supervisor_decision', '')

        if 'final_response' in state:
            return END
        if "maximo" in decision:
            return "maximo"
        elif "vector_db" in decision:
            return "vector_db"
        elif 'unknown' in decision:
            return "unknown"
        