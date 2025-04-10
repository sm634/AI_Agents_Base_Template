"""
Base Agent class, that can be inherited to create other agents.
In this framework or design what determines or separates each agent are the following:
    1. The LLM or model which embodies the core agent.
    2. The system prompt (which highlights the overall task the agent is made to do).
    3. The Tools that the agent has access to.
"""


from typing import Dict, Any, Optional, List, Annotated
from pydantic import BaseModel
from config import Config
from langchain_core.messages import SystemMessage, HumanMessage
import operator

# ----- Shared State Schema -----
class AgentState(BaseModel):
    user_input: str
    supervisor_decision: Optional[str] = None
    maximo_payload: Optional[str] = None
    maximo_agent_response: Optional[str] = None
    vector_search_result: Optional[str] = None
    memory_chain: Annotated[List[Dict[str, Any]], operator.add] = []


class BaseAgent:
    def __init__(self, name="BaseAgent"):
        # Agent metadata.
        self.name = name # name of the agent.
        self.description = "BaseAgent to be inherited by other custom agents with base attributes."
        
        # System and user input message to be defined for child agents based on task and user input.
        self.system_message = SystemMessage("")
        self.user_input = HumanMessage("")

        # set agent hyperparameters. Override in custom agents.
        self.agent_params = Config.base_agent_params
        self.model_id = self.agent_params['model_id']
        self.model_params = self.agent_params['model_parameters']

        self.llm = None # a choice of your LLM object to be instantiated here.

        self.tools = self.agent_params['tools']


    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return self.handle_input(state)

    def handle_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
