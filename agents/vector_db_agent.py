from prompt_reference.vector_db_agent_prompts import vector_db_prompt
from tools.vector_db_tools import vectorDbAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config
import streamlit as st
from langgraph.graph import END

class VectorDbAgent(BaseAgent):
    def __init__(self, name="vector_db_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.vector_db_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            vectorDbAgentTools.similarity_search
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)    
            
        self.response_agent = Config.vector_db_agent_params
        self.response_agent = get_llm(self.response_agent)

    def handle_input(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = vector_db_prompt.format(state=state)
        message = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"{state['user_input']}")
        ]
        # call the llm with the message
        agent_response = self.llm_with_tools.invoke(message)


        # update the state with the agent response
        if hasattr(agent_response, 'tool_calls'):
            try:
                state['tool_calls'] = agent_response.tool_calls[0]['name']
            except IndexError:
                pass

        return state
    
    def handle_output(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = vector_db_prompt.format(state=state)
        message = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"{state['user_input']}")
        ]
        # call the llm with the message
        agent_response = self.response_agent.invoke(message)

        # update the state with the agent response
        state['final_response'] = agent_response.content
        state['memory_chain'].append({
            'final_response': state['final_response']
        })
        return state

    def vector_search(self, state: AgentState):
        # check the tool to use.
        selected_tool = "similarity_search"
        print(f"Calling: {selected_tool}")

        if selected_tool == "similarity_search":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "query": state['user_input'],
                "k": 3 # state['top searches']
            }

            # invoke the tool and get the result.
            vector_db_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['vector_db_agent_response'] = vector_db_agent_response
            state['memory_chain'].append({
                'vector_db_agent_response': state['vector_db_agent_response']
            })

        return state
    

    def router(self, state: AgentState):
        """
        The router function to route the agent to the next step.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """
        if state['tool_calls'] == "similarity_search":
            return "vector_search"        
        else:
            return END
