from prompt_reference.vector_db_agent_prompts import vector_db_prompt
from tools.vector_db_tools import VectorAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config


class ChromaAgent(BaseAgent):
    def __init__(self, name="vector_db_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.vector_db_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            VectorAgentTools.search
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)        


    def handle_input(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        while state['vector_db_agent_response'] == "":
            system_msg = vector_db_prompt.format(state=state)
            message = [
                SystemMessage(content=system_msg),
                HumanMessage(content=f"{state['user_input']}")
            ]
            # call the llm with the message
            agent_response = self.llm_with_tools.invoke(message)

            # update the state with the agent response
            state.setdefault('tool_calls', '')
            if hasattr(agent_response, 'tool_calls'):
                state['tool_calls'] = agent_response.tool_calls[0]['name']
                state = self.use_vector_db_tools(state=state)
            else:
                break

        return {'vector_db_agent_response': state['vector_db_agent_response']}
    

    def use_vector_db_tools(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")
        # invoke the tools and udpate the states depending on the tool use.
        if selected_tool == "search":
            # set the input parameters or arguments for the tool.
            tool_input = {
                "user_input": state['user_input']
            }

            # invoke the tool and get the result.
            vector_db_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['vector_db_agent_response'] = vector_db_agent_response
            state['memory_chain'].append({
                'vector_db_agent_response': state['vector_db_agent_response']
            })

        return state


class MilvusAgent(BaseAgent):
    def __init__(self, name="vector_db"):
        
        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.maximo_agent_params
        self.llm = get_llm(self.agent_params)

        self.system_message = SystemMessage(content="""You are a milvus expert. Use the tools at your disposable to search for data related to the user query as best you can.""")

    def handle_input(self, state: AgentState):
        raise NotImplementedError