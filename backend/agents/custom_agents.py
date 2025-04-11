from typing import Dict, Any,Annotated
from pydantic import BaseModel

from agents.base_agent import BaseAgent, AgentState
from connectors.maximo_connector import MaximoConnector

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx
from langchain_core.runnables import Runnable
from langchain_core.tools import tool

from config import Config
import os
import ast


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
        self.payload_generator_model_id = self.payload_generator_params['model_id']
        self.payload_generator_model_params = self.payload_generator_params['model_parameters']
        self.payload_generator_llm = ChatWatsonx(   
            model_id=self.payload_generator_model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.payload_generator_model_params
            )
        # define the system message for the payload generator.
        self.payload_generator_system_message = SystemMessage(content="""You are a Maximo expert. Your job is to translate human or user query into a maximo
                                    payload that can be used to make an API Get or Post request. When you receive the human
                                    query, you should generate a well-formed payload format. Use the examples to help you. The formats are based on whether or not 
                                    the query is best served by a get or post request.
                                    Once you decide on the operation type, such as Get or Post, you should generate a well-formed payload that can be provided as params to make an api call for the correct request type.
                                    If the query does not have all the required information, use the examples below along with the information from the query to help you.
                                    Always generate a consistent well-formed payload as a response, like in the example. The <example-get></example-get> provies making queries to the Maximo API that only retrieves data
                                    and answers the user query. While the <example-post></example-post> provides making queries to the Maximo API that updates, modifies or changes data in the Maximo database. Make sure you
                                    use the correct request type based on what the user is asking and format the correct payload. 
                                    <example-get>
                                    user_input: What is the status, description and priority of work order number 5012?
                                    response: {
                                                "request_type": "get",
                                                "params": {
                                                    "oslc.where": "wonum=5012",
                                                    "oslc.select": "wonum,description,wopriority,createdby,workorderid,status",
                                                    "lean": "1",
                                                    "ignorecollectionref": "1"
                                                    }
                                                }
                                    </example-get>
                                    <example-post>
                                    user_input: Make a change to the work order priority and change the site to Bedford.
                                    response: {
                                                "request_type": "post",
                                                "params": {
                                                    "wopriority": "1",
                                                    "siteid": "BEDFORD"
                                                    }
                                                }
                                    </example-post>
                                    Only provide the payload that can be sent to the Maximo API. Ensure it is a valid json.
                                    Do not provide any other information or explanation.
                                    If the user input is not related to Maximo, send back a response with 
                                    {
                                        "params": {
                                            "message": "This query is not related to Maximo."
                                        }
                                    }.
                                    Now classify the type of request the user is making and generate the associated params in json.
                                    <response>""")
    


        # instantiate the parameters for the agent.
        self.agent_params = Config.maximo_agent_params
        self.model_id = self.agent_params['model_id']
        self.model_params = self.agent_params['model_parameters']
        self.llm = ChatWatsonx(
            model_id=self.model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.model_params
            )
        
        # define the tools that the agent will have access to.
        self.tools = [self.get_maximo_wo_details, self.update_maximo_wo_details]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # define the system message for the agent.
        self.system_message = SystemMessage(content="""You are a Maximo expert. You are provided with two tools:
                                            1. get_maximo_wo_details(state: AgentState) - For retrieving Maximo work order details.
                                            2. update_maximo_wo_details(state: AgentState) - For updating or posting changes to a Maximo work order.
                                            Given a user query, determine which tool to invoke, and use it with the `state` object provided. You do NOT need to return the payload itself—just the result of the correct tool call. Always use one of the tools.
                                            """)


    def generate_maximo_payload(self, state: AgentState) -> Dict[str, Any]:
        """
        Generates the Maximo payload based on the user input.
        :param state: The state of the agent containing the user input and to be updated.
        :return: A dictionary containing the Maximo payload.
        """
        # Check if the user input is classified as a Maximo operation
        user_input = HumanMessage(
            content=f"{state.user_input}"
        )
        messages = [
            self.payload_generator_system_message,
            user_input,
        ]

        response = self.payload_generator_llm.invoke(messages)
        state.maximo_payload = response.content
        # Update the state memory_chain
        state.memory_chain.append({
            "maximo_payload": state.maximo_payload
        })
    
        return state

    # @tool(description="Perform a get request with Maximo API.")
    def get_maximo_wo_details(self, state: Annotated[AgentState, "Agent state containing user input and payload"]) -> dict:
        """
        Performs the Maximo get request based on the generated payload.
        :param state: The state of the agent containing the maximo_payload.
        :return: A dictionary containing the Maximo operation result."""
        payload = ast.literal_eval(state.maximo_payload)
        params = payload.get("params")

        result = self.maximo_connector.get_workorder_details(params)

        # update the result
        state.maximo_agent_response = result
        # Update the state memory_chain
        state.memory_chain.append({
            "input": state.user_input,
            "operation": 'get_maximo_wo_details',
            "maximo_result": result
        })

        return result
        
    # @tool(description="Perform a Post or update request with Maximo API.")
    def update_maximo_wo_details(self, state: Annotated[AgentState, "Agent state containing user input and payload"]) -> Dict[str, Any]:
        """
        Performs a Post or update request based on the generated payload.
        :param state: The state of the agent containing the maximo_payload.
        :return: A dictionary containing the Maximo operation result."""
        payload = ast.literal_eval(state.maximo_payload)
        params = payload.get("params")

        result = self.maximo_connector.post_workorder_details(params)
        # update the result
        state.maximo_agent_response = result
        # Update the state memory_chain
        state.memory_chain.append({
            "input": state.user_input,
            "operation": 'update_maximo_wo_details',
            "maximo_result": result
        })


        return result
    
    def perform_maximo_operation(self, state: AgentState):
        """
        Uses the maximo tools at the llm with tools to perform the maximo operation.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: A dictionary containing the Maximo payload.
        """
        # Check to see the maximo payload returned, and the response type to perform the correct action.
        payload = ast.literal_eval(state.maximo_payload)
        request_type = payload.get("request_type")
        params = payload.get("params")

        if request_type.lower() == 'get':
            result = self.maximo_connector.get_workorder_details(params)
        elif request_type.lower() == 'post':
            result = self.maximo_connector.post_workorder_details(params)
        else:
            result = {
                "message": "This query is not related to Maximo."
            }
        # Update the state memory_chain
        # update the result
        state.maximo_agent_response = result
        # Update the state memory_chain
        state.memory_chain.append({
            "maximo_result": result
        })

        return state

def handle_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("supervisor_decision") == "maximo":
        messages = self.prompt.format_messages(query=state["user_input"])
        response = self.llm.invoke(messages)
        state["maximo_response"] = response.content
    return state


class VectorDBAgent(BaseAgent):
    def __init__(self, name="vector_db"):
        
        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.maximo_agent_params
        self.model_id = self.agent_params['model_id']
        self.model_params = self.agent_params['model_parameters']
        self.llm = ChatWatsonx(
            model_id=self.model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.model_params
            )
        self.tools = self.agent_params['tools']
        self.llm = self.llm.bind_tools(self.tools)

        self.system_message = SystemMessage(content="""You are a Maximo expert. Your job is to translate human or user query into a maximo
                                            payload that can be sent across as part of an API Get or Post request. When you receive the human
                                            query, you should decide if a maximo operation is required to send a Get or Post request to action or
                                            answer the query to the maximo database. Use the tool at your disposal to decide if to use request_type: get or post and what payload
                                            you should pass to the tool function you have at your disposal.
                                            Once you decide on the operation type, such as Get or Post, you should generate a json or python dictionary that fulfills the query.
                                            If the query does not have all the required information, use the example below to and the information from the query
                                            the best you can to generate a consistent response, like in the example.
                                            Use the examples below to help you. 
                                            <example-get>
                                            user_input: What is the status, description and priority of work order number 5012?
                                            response: {
                                                        request_type: "get",
                                                        params: {
                                                            "oslc.where": "wonum=5012",
                                                            "oslc.select": "wonum,description,wopriority,createdby,workorderid,status",
                                                            "lean": lean,
                                                            "ignorecollectionref": ignorecollectionref
                                                            }
                                                        }
                                            </example-get>
                                            <example-post>
                                            user_input: Make a change to the work order priority and change the site to Bedford.
                                            response: {
                                                        request_type: "post",
                                                        params = {
                                                            "wopriority": "1",
                                                            "siteid": "BEDFORD"
                                                            }
                                                        }
                                            </example-post>
                                            Now classify the type of request the user is making and generate the associated params in json.
                                            user_input: {user_input}
                                            response:""")

    def handle_input(self, state: BaseModel):
        if state.get("supervisor_decision") == "vector_db":
            messages = "To be implemented"
            state.vector_search_result = messages
        return state
