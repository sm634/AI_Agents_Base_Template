from prompt_reference.postgres_agent_prompts import postgres_prompt, sql_query_prompt
from tools.postgres_agent_tools import PostGresAgentTools

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from config import Config
from connectors.db_connector import PostgresConnector  # Add this import or adjust the path as needed


class PostGresAgent(BaseAgent):
    def __init__(self, name="postgres_agent"):

        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.postgres_agent_params
        self.llm = get_llm(self.agent_params)

        # define and bind the tools to the agent.
        self.tools = [
            PostGresAgentTools.generate_query,
            PostGresAgentTools.validate_sql_query,
            PostGresAgentTools.run_query
            ]

        # the tools_dict enables the agent to call the tools by name.
        self.tools_dict = {t.name: t for t in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # define the system message for the sql query generation agent.
        self.sql_generator_params = Config.sql_generator_params
        self.sql_generator = get_llm(self.sql_generator_params)       


    def handle_input(self, state: AgentState):
        """
        Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: updated state for the agent.
        """

        # use the tools to get the results and responses before getting back to the supervisor.
        system_msg = postgres_prompt.format(state=state)
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
    

    def generate_sql_query(self, state: AgentState):
        # check the tool to use.
        selected_tool = "generate_query"
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

        except Exception as e:
            state['agent_tool_retries'] += 1
            pass


    def validate_sql_query(self, state: AgentState):
        """ Validate the SQL query using pglast.
        :param state: The state of the agent containing the SQL query to validate.
        :return: updated state with validation result.
        """
        # Extract the SQL query from the state
        sql_query = state['postgres_query']
        # fetching propery query using regular expression
        query = re.search(r"SELECT.*;|UPDATE.*;|INSERT.*;", sql_query)

        # Validate the SQL query using pglast
        response = PostgresConnector.validate_with_pglast_Latest(sql=query.group(0) if query else sql_query)
        # Check if the response indicates an error
        if response.get("status") == "error":
            # If there's an error, update the state with the error message
            state['postgres_agent_response'] = response
            state['memory_chain'].append({
                'validation_error': response.get("error", "Unknown error")
            })
            return state
        # If validation is successful, update the state with the validation result
        if response.get("status") == "ok":
            response = {
                "status": "ok",
                "message": "SQL query is valid."
            }
        else:
            response = {
                "status": "error",
                "error": "SQL query validation failed."
            }
        
        # Update the state with the validation result
        state['postgres_agent_response'] = response
        # Append the validation result to the memory chain
        state['memory_chain'].append({
            'validation_response': response
        })
        # Return the updated state
        return state
