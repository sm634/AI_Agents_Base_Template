from typing import Dict, Any,Annotated
from pydantic import BaseModel

from agents.base_agent import BaseAgent, AgentState
from connectors.maximo_connector import MaximoConnector

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx

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


    def generate_maximo_payload(self, state: AgentState) -> Dict[str, Any]:
        """
        Generates the Maximo payload based on the user input.
        :param state: The state of the agent containing the user input and to be updated.
        :return: A dictionary containing the Maximo payload.
        """
        # Check if the user input is classified as a Maximo operation
        user_input = HumanMessage(
            content=f"{state['user_input']}"
        )
        messages = [
            self.payload_generator_system_message,
            user_input,
        ]

        response = self.payload_generator_llm.invoke(messages)
        state['maximo_payload'] = response.content
        # Update the state memory_chain
        state['memory_chain'].append({
            "maximo_payload": state['maximo_payload']
        })
    
        return {
            "maximo_payload": state['maximo_payload']
        }
    
    def perform_maximo_operation(self, state: AgentState):
        """
        Uses the maximo tools at the llm with tools to perform the maximo operation.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: A dictionary containing the Maximo payload.
        """
        # Check to see the maximo payload returned, and the response type to perform the correct action.
        payload = ast.literal_eval(state['maximo_payload'])
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

        # update the result
        state['maximo_agent_response'] = result
        # Update the state memory_chain
        state['memory_chain'].append({
            "maximo_result": result
        })

        return {
            "maximo_agent_response": result
        }


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

