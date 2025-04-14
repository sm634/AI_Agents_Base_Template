from typing import Dict, Any

from agents.base_agent import BaseAgent, AgentState
from connectors.maximo_connector import MaximoConnector
from prompt_reference.maximo_agent_prompts import MaximoAgentPrompts
from tools.maximo_agent_tools import MaximoAgentTools
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage

from config import Config


class MaximoAgent(BaseAgent):
    def __init__(self, name="maximo"):
        """
        An agent specialised on performing operations on Maximo.
        """
        super().__init__(name)

        # instantiate maximo connector.
        self.maximo_connector = MaximoConnector()

        # instantiate the parameters for the payload generator.
        self.payload_generator_params = Config.maximo_payload_generator_params
        self.payload_generator_llm = get_llm(self.payload_generator_params)
        
        # define the system message for the payload generator.
        self.payload_generator_system_message = SystemMessage(content=MaximoAgentPrompts.payload_generator_prompt)

        # instantiate the parameters for the agent.
        self.agent_params = Config.maximo_agent_params
        self.llm = get_llm(self.agent_params)
        
        # define and bind the tools to the agent.
        self.tools = [
                MaximoAgentTools.generate_maximo_payload, 
                MaximoAgentTools.perform_maximo_operation
                 ]
        
        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        

    def handle_input(self, state: AgentState) -> Dict[str, Any]:
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: A dictionary containing the action taken.
        """
        system_message = MaximoAgentPrompts.maximo_agent_prompt.format(state=state)
        message = [
            SystemMessage(content=system_message),
            HumanMessage(content=f"{state['user_input']}")
        ]
        
        # call the llm with the message.
        agent_response = self.llm_with_tools.invoke(message)

        # update the state with the agent response
        state.setdefault('tool_calls', []).append(agent_response.tool_calls)
        state.setdefault('memory_chain', []).append({
            'tool_calls': state['tool_calls'],
        })

        # Check if the user input is classified as a Maximo operation
        for tool_call in agent_response.tool_calls:
            selected_tool = tool_call['name'] 
            print(f"Calling: {tool_call['name']}")
            # invoke the tools and update the states depending on each tool use.
            if selected_tool == "perform_maximo_operation":
                # set the input parameters or arguments for the tool.
                tool_input = {
                    "maximo_payload": state['maximo_payload'],
                    }

                # invoke the tool and get the result.
                maximo_agent_response = self.tools_dict[selected_tool].invoke(tool_input)
                # update the state with the tool result.
                state['maximo_agent_response'] = maximo_agent_response
                state['memory_chain'].append({
                    'maximo_agent_response': agent_response,
                })

                return {
                    "maximo_agent_response": maximo_agent_response,
                    "next": "supervisor",
                    }

            elif selected_tool == "generate_maximo_payload":
                # set the input parameters or arguments for the tool.
                tool_input = {
                    "user_input": state['user_input'],
                    "system_prompt": self.payload_generator_system_message,
                    "llm": self.payload_generator_llm
                }
                # invoke the tool and get the result.
                maximo_payload = self.tools_dict[selected_tool].invoke(tool_input)
                # update the state with the tool result.
                state['maximo_payload'] = maximo_payload
                state['memory_chain'].append({
                    'maximo_payload': state['maximo_payload'],
                })
                
                return {
                    "maximo_payload": maximo_payload,
                    "next": "maximo_agent"
                    }
