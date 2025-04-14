"""
A set of custom Agents to be implemented here. They inheret from the BaseAgent.
"""

# native python
import os
# repo specific modules and libraries
from config import Config
from agents.base_agent import BaseAgent, AgentState
from prompt_reference.supervisor_prompt import SupervisorPrompts
from tools.supervisor_tools import SupervisorTools
from utils.handle_configs import get_llm
# third party libraries
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx



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
        if 'maximo_agent_response' not in state:
            state['maximo_agent_response'] = ''
        if 'milvus_agent_response' not in state:
            state['milvus_agent_response'] = ''
        else:
            state['milvus_agent_response'] = state['milvus_agent_response']
            state['maximo_agent_response'] = state['maximo_agent_response']
        
        agent_response = state['maximo_agent_response'] + '\n' + state['milvus_agent_response']

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
        state['supervisor_decision'] = supervisor_response
        state.setdefault('memory_chain',[]).append(
            {
                'supervisor_decision': state['supervisor_decision']
            }
        )

        if state['supervisor_decision'] in ['maximo', 'milvus', 'unknown']:
            return {
                "supervisor_decision": state['supervisor_decision']
            }
        else:
            if 'final_response' not in state:
                state['final_response'] = ''

            state['final_response'] = supervisor_response
            return {
                "final_response": state['final_response']
            }
        
    @staticmethod
    def router(state: AgentState):
        print("Routing to the ")
        next = ''
        if "maximo" in state['supervisor_decision']:
            next = "maximo"
        elif "milvus" in state['supervisor_decision']:
            next = "milvus"
        else:
            next = "supervisor"
        return {
            "supervisor_decision": next
        }
        