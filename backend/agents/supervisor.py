"""
A set of custom Agents to be implemented here. They inheret from the BaseAgent.
"""

# native python
from typing import Dict, Any
import os
# repo specific modules and libraries
from config import Config
from agents.base_agent import BaseAgent, AgentState
# Exotic libraries
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import ChatWatsonx
from pydantic import BaseModel

from dotenv import load_dotenv
_ = load_dotenv()


class SupervisorAgent(BaseAgent):
    def __init__(self, name:str="supervisor"):
        """A supervisor agent, which is used to route or delgate user query to other agents best able to assist with the query.
        :state: pydantic.BaseModel: The state that the agent will have access to for reading and updating. It is 
        """

        super().__init__(name)

        # instantiate the parameters for the agent. 
        self.router_params = Config.supervisor_router_params
        self.model_id = self.router_params['model_id']
        self.model_params = self.router_params['model_parameters']
        self.llm = ChatWatsonx(
            model_id=self.model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.model_params
            )


        self.router_system_message = SystemMessage(content="""You are a routing agent. Route the query to 'maximo', 'vector_db', or 'unknown' based on which source the query is best answered by. 
                                            To help you make that decision, look for key words in the query that is most closely associated to one of those systems.
                                            Ensure that You only provide single word answer with one of the following: 'maximo', 'vector_db', 'unknown'.
                                            Use the examples below to help you.
                                            <example>
                                            user_input: How many assets have been reported damaged over the past three days for customer x?
                                            response: maximo
                                            </example>
                                            <example2>
                                            user_input: Which documents will help me troubleshoot a problem regarding orders in the system?
                                            response: vector_db
                                            </example2>
                                            <example3>
                                            user_input: How do I get to the coventry?
                                            response: unknown.
                                            </example3>
                                            Now classify the user input below.
                                            user_input: {user_input}
                                            response:""")


    def classify_query(self, state: AgentState) -> str:
        user_input = HumanMessage(
            content=f"{state.user_input}"
        )
        messages = [
            self.router_system_message,
            user_input
        ]
        response = self.llm.invoke(messages)
        return response

    def evaluate_response(self, user_input: str, response: str) -> bool:
        messages = self.evaluation_prompt.format_messages(query=user_input, response=response)
        result = self.llm.invoke(messages)
        return "yes" in result.content.strip().lower()

    def handle_input(self, state: AgentState):
        decision = self.classify_query(state.user_input.content)
        state.supervisor_decision = decision
        state.memory_chain.append({
            "input": state.user_input,
            "decision": decision,
            "output": "PENDING"
        })
        return state

    def postprocess(self, state: Dict[str, Any]) -> Dict[str, Any]:
        output = state.get("maximo_response") or state.get("vector_search_result")
        success = self.evaluate_response(state["user_input"], output)
        state["memory_chain"][-1]["output"] = output
        state["memory_chain"][-1]["success"] = success
        return state
