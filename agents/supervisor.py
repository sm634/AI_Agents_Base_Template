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


class SupervisorAgent(BaseAgent):
    def __init__(self, name:str="supervisor"):
        """A supervisor agent, which is used to route or delgate user query to other agents best able to assist with the query.
        :state: pydantic.BaseModel: The state that the agent will have access to for reading and updating. It is 
        """

        super().__init__(name)

        # instantiate the parameters for router part of the agent. 
        self.router_params = Config.supervisor_router_params
        self.model_id = self.router_params['model_id']
        self.model_params = self.router_params['model_parameters']
        self.router_llm = ChatWatsonx(
            model_id=self.model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.model_params
            )


        self.router_system_message = SystemMessage(content="""You are an excellent routing agent. Route the query to 'maximo', 'vector_db', or 'unknown' based on which source the query is best answered by. 
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
        
        # instantiate the parameters for the evaluation part of the agent.        # instantiate the parameters for router part of the agent. 
        self.evaluator_params = Config.supervisor_evaluator_params
        self.model_id = self.evaluator_params['model_id']
        self.model_params = self.evaluator_params['model_parameters']
        self.evaluator_llm = ChatWatsonx(
            model_id=self.model_id,
                url=os.environ["WATSONX_URL"],
                apikey=os.environ["IBM_CLOUD_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
                params=self.model_params
            )
        
        self.evaluation_prompt = SystemMessage(content="""You are an excellent supervisor and a friendly customer facing assistant. 
                                                You are tasked with evaluating the response from an agent.
                                                You will receive a user input and the response from an agent. 
                                                Your job is to evaluate if the response is suitably relevant to the user input or query.
                                                If the response has relevant answers to the query, ensure it is expressed in a very friendly style to be provided to the human user.
                                                If the response is not relevant to the user input, provide the answer in a friendly style to the user, and if there are some pieces of information in the query from the user that could help in answering the query. Gently nudge them to provide it.
                                                response_to_evaluate: {response}
                                                evaluation:""")


    def supervisor_router(self, state: AgentState) -> str:
        user_input = HumanMessage(
            content=f"{state['user_input']}"
        )
        messages = [
            self.router_system_message,
            user_input
        ]
        response = self.router_llm.invoke(messages)
        if 'maximo' in response.content.lower():
            state['supervisor_decision'] = "maximo"
        elif 'vector_db' in response.content.lower():
            state['supervisor_decision'] = "vector_db"
        else:
            state['supervisor_decision'] = "unknown"
        state['supervisor_decision'] = response.content.lower()
        state['memory_chain'].append({
            "input": state['user_input'],
            "supervisor_decision": state['supervisor_decision'],
        })

        return {
            "supervisor_decision": state['supervisor_decision']
        }


    def supervisor_evaluation(self, state: AgentState) -> bool:
        user_input = HumanMessage(
            content=f"{state['user_input']}"
        )
        messages = [
            self.evaluation_prompt,
            user_input,
            HumanMessage(content=f"{state['maximo_agent_response'] or state['vector_search_result']}")
        ]
        result = self.evaluator_llm.invoke(messages)
        # update the state with the evaluation result.
        state['memory_chain'].append({
            'final_response': result.content
        })
        state['memory_chain'][-1]["output"] = result.content
        return {
            "evaluation": result.content
        }
