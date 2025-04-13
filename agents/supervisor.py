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
        
        # define and bind the tools to the agent.
        self.tools = [
            SupervisorTools.supervisor_router,
            SupervisorTools.supervisor_evaluation
        ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # instantiate the router llm agent with params.
        self.router_params = Config.supervisor_router_params
        self.router_llm = get_llm(self.router_params)

        # instantiate the evaluation llm agent with params.
        self.evaluation_params = Config.supervisor_evaluator_params
        self.evaluation_llm = get_llm(self.evaluation_params)


    def handle_input(self, state: AgentState):
        """To be implemented"""
        # instantiate the prompt with the state.
        system_message = SupervisorPrompts.supervisor_prompt.format(state=state)
        message = [
            SystemMessage(content=system_message),
            HumanMessage(content=state['user_input'])
        ]

        # call the llm with the message.
        supervisor_response = self.llm_with_tools.invoke(message)

        for tool_call in supervisor_response.tool_calls:
            selected_tool = self.tools_dict[tool_call['name']]
            print(f"Calling: {tool_call['name']}")

            # call the tool with the arguments.
            if selected_tool.name == "supervisor_router":

                # set up the system prompt template for the router.
                router_prompt = SupervisorPrompts.routing_prompt.format(user_input=state['user_input'])
                
                # set up the tool input.
                tool_input = {
                    "user_input": state['user_input'],
                    "llm": self.router_llm,
                    "router_prompt": SystemMessage(router_prompt)
                }
                
                # invoke the tool.
                tool_response = selected_tool.invoke(tool_input)

                # update the state with the tool response.
                state['supervisor_decision'] = tool_response
                state.setdefault('memory_chain', []).append({
                    'supervisor_decision': state['supervisor_decision']
                })

            elif selected_tool.name == "supervisor_evaluation":
                # set up the system prompt template for the evaluation.
                evaluation_prompt = SupervisorPrompts.evaluation_prompt.format(
                    user_input=state['user_input'],
                    agent_response=state['maximo_agent_response'] or state['milvus_agent_response'])
                
                # set up the tool input.
                tool_input = {
                    "user_input": state['user_input'],
                    "agent_response": state['maximo_agent_response'] or state['milvus_agent_response'],
                    "llm": self.evaluation_llm,
                    "evaluation_prompt": SystemMessage(evaluation_prompt)
                }

                # invoke the tool.
                tool_response = selected_tool.invoke(tool_input)
                # update the state with the tool response.
                state['supervisor_decision'] = tool_response
                state['memory_chain'].append({
                    'final_response': tool_response
                })        

        # update the states.

        return {
            "supervisor_decision": tool_response
        }