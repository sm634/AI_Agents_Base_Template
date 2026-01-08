from prompt_reference.r_general_agent_prompts import general_prompt
from prompt_reference.postgres_agent_prompts import sql_query_prompt
from tools.report_generatorC_tools import generate_reports_tools
from tools.postgres_agent_tools import PostGresAgentTools
from tools.vector_db_tools import vectorDbAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from config import Config


class GeneralAgent(BaseAgent):
    def __init__(self, name="general_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.general_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            PostGresAgentTools.generate_query,
            PostGresAgentTools.run_query,
            vectorDbAgentTools.similarity_search,
            generate_reports_tools,
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # define the system message for the sql query generation agent.
        self.sql_generator_params = Config.sql_generator_params
        self.sql_generator = get_llm(self.sql_generator_params)

        # define the agent for output handling.
        self.response_agent = Config.general_agent_response_params
        self.response_agent = get_llm(self.response_agent)


    def handle_input(self, state: AgentState):
        """
        Selects the correct tool to use for the user input or ask.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = general_prompt.format(state=state)
        message = [
            SystemMessage(content=system_msg),
            HumanMessage(content=f"{state['user_input']}")
        ]
        # call the llm with the message for its reasoning and decision making.
        agent_response = self.llm.invoke(message)
        # update the state with the agent response
        state['supervisor_decision'] = agent_response.content
        state['memory_chain'].append({
            'supervisor_decision': agent_response.content}
        )

        # get the llm response and update the state with tool calls.
        tool_response = self.llm_with_tools.invoke(message)

        # update the state with the agent response
        if hasattr(tool_response, 'tool_calls'):
            try:
                state['tool_calls'] = tool_response.tool_calls[0]['name']
                state['memory_chain'].append({
                'selected_tool': state['tool_calls']
                })
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
        system_msg = general_prompt.format(state=state)
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
    
    def generate_report(self, state: AgentState):
        # check the tool to use.
        selected_tool = "generate_reports_tools"
        print(f"Calling: {selected_tool}")
        # invoke the tools and udpate the states depending on the tool use.
        # if selected_tool == "generate_reports_tools":
        # set the input parameters or arguments for the tool.
        tool_input = {
            "query": state['postgres_query']
        }

        # invoke the tool and get the result.
        report_generation_response = self.tools_dict[selected_tool].invoke(tool_input)

        # update the state with the tool result.
        state['report_generation_response'] = report_generation_response
        state['memory_chain'].append({
            'report_generation_response': state['report_generation_response']
        })

        return state
    

    def vector_search(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
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

    def generate_sql_query(self, state: AgentState):
        # check the tool to use.
        selected_tool = state['tool_calls']
        print(f"Calling: {selected_tool}")

        system_prompt = sql_query_prompt.format(user_input=state['user_input'])

        system_prompt = SystemMessage(
            content=system_prompt
        )
        # set the input parameters or arguments for the tool.
        tool_input = {
            "user_input": state['user_input'],
            "system_prompt": system_prompt,
            "llm": self.sql_generator
        }
        
        # invoke the tool and get the result.
        try:
            sql_query = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['postgres_query'] = sql_query
            state['memory_chain'].append({
                'postgres_query': state['postgres_query']
            })
        except:
            state['agent_tool_retries'] += 1
            pass

        return state
    
    def run_sql_query(self, state: AgentState):
        # check the tool to use.
        print(f"Running SQL Query: {state['postgres_query']}")
        selected_tool = 'run_query'

        # set the input parameters or arguments for the tool.
        tool_input = {
            "query": state['postgres_query'],
            "params": None
        }

        try:
            # invoke the tool and get the result.
            postgres_agent_response = self.tools_dict[selected_tool].invoke(tool_input)

            # update the state with the tool result.
            state['postgres_agent_response'] = postgres_agent_response
            state['memory_chain'].append({
                'postgres_agent_response': state['postgres_agent_response']
            })
        except:
            state['agent_tool_retries'] += 1
            pass

        return state
    

    def router(self, state: AgentState):
        """
        The router function to route the agent to the next step.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """
        # If the agent has decided to generate a SQL query, we will call the sql query generation tool.
        if state['tool_calls'] == "generate_query":
            return "generate_sql_query"
        # if the agent has decided to do a similarity search, we will call the vector db search tool.    
        elif state['tool_calls'] == "similarity_search":
            return "vector_search"
        else:
            END

    
    def router_2(self, state: AgentState):
        """
        The router function to route the agent to the next step after the tool calls.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """
        # If the agent has decided to generate a SQL query, we will call the sql query generation tool.
        if "report" in state['user_input'].lower():
            print("report" in state['user_input'].lower())
            state['report_generation_requested'] = True
            state['memory_chain'].append({
                'report_generation_requested': state['report_generation_requested']
            })
            return "generate_report" 
        else:            
            return "run_query"
        