from connectors.maximo_connector import MaximoConnector

from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool
import ast
from langchain_core.messages import HumanMessage, SystemMessage

# instantiate maximo connector.
maximo_connector = MaximoConnector()


class MaximoAgentTools:

    class MaiximoPayloadInput(BaseModel):
        maximo_payload: Union[Dict, str] = Field(description="The payload to be sent to Maximo.")

    @tool(args_schema=MaiximoPayloadInput)
    def perform_maximo_operation(maximo_payload: Union[Dict, str]):
        """
        Perform maximo operation for API requests.
        :maximo_payload: The payload to be sent as argument to make the API request to Maximo.
        :return: A dictionary containing the Maximo payload.
        """
        # Check to see the maximo payload returned, and the response type to perform the correct action.
        if isinstance(maximo_payload, str):
            maximo_payload = ast.literal_eval(maximo_payload)

        request_type = maximo_payload.get("request_type")
        params = maximo_payload.get("params")

        if request_type.lower() == 'get':
            result = maximo_connector.get_workorder_details(params)
        elif request_type.lower() == 'post':
            result = maximo_connector.post_workorder_details(params)
        else:
            result = {
                "message": "This query is not related to Maximo."
            }

        return {
            "maximo_agent_response": result
        }
    

    class MaximoPayloadGeneratorInput(BaseModel):
        user_input: str = Field(description="Thing to search for")
        system_prompt: SystemMessage = Field(description="System prompt to use for generating the payload")
        llm: Any = Field(description="LLM to use for generating the payload")


    @tool(args_schema=MaximoPayloadGeneratorInput)
    def generate_maximo_payload(user_input, system_prompt, llm) -> Dict[str, Any]:
        """
        Generates the Maximo payload based on the user input.
        :param user_input: The user_input.
        :param system_prompt: The system prompt to use for generating the payload.
        :param llm: The LLM to use for generating the payload.
        :return: A dictionary containing the Maximo payload.
        """
        # Check if the user input is classified as a Maximo operation
        user_input = HumanMessage(
            content=user_input
        )
        messages = [
            system_prompt,
            user_input,
        ]

        response = llm.invoke(messages)

        # validate do a dict.
        maximo_payload = ast.literal_eval(response.content)

        return maximo_payload
