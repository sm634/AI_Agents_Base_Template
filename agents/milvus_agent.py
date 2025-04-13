from typing import Dict, Any

from agents.base_agent import BaseAgent, AgentState
from utils.handle_configs import get_llm

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx

from config import Config

class MilvusAgent(BaseAgent):
    def __init__(self, name="vector_db"):
        
        super().__init__(name)

        # instantiate the parameters for the agent.
        self.agent_params = Config.maximo_agent_params
        self.llm = get_llm(self.agent_params)

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

    def handle_input(self, state: AgentState) -> Dict[str, Any]:
        """Takes action based on the state of the agent.
        :param state: The state of the agent containing the user input and states to be updated.
        :return: A dictionary containing the action taken.
        """
        state['milvus_agent_response'] = "This is just a message from the milvus agent. I am not ready to work yet."
        response = "This is just a message from the milvus agent. I am not ready to work yet."
        return {"milvus_agent_response": state['milvus_agent_response']}