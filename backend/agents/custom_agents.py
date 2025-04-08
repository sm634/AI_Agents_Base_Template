from typing import Dict, Any
from pydantic import BaseModel
from agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate


class MaximoAgent(BaseAgent):
    def __init__(self, state: BaseModel, name="maximo"):
        super().__init__(name)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Maximo agent. Help the user with work orders and asset management."),
            ("human", "{query}")
        ])

    def handle_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if state.get("supervisor_decision") == "maximo":
            messages = self.prompt.format_messages(query=state["user_input"])
            response = self.llm.invoke(messages)
            state["maximo_response"] = response.content
        return state


class VectorDBAgent(BaseAgent):
    def __init__(self, state: BaseModel, name="vector_db", llm=None):
        super().__init__(name, llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a vector database agent. Answer based on semantic search."),
            ("human", "{query}")
        ])

    def handle_input(self, state: BaseModel):
        if state.get("supervisor_decision") == "vector_db":
            messages = self.prompt.format_messages(query=state["user_input"])
            response = self.llm.invoke(messages)
            state["vector_search_result"] = response.content
        return state
