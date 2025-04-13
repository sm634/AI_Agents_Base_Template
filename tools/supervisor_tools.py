from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool
from langchain_core.messages import HumanMessage, SystemMessage


class SupervisorTools:


    class SupervisorRouterInput(BaseModel):
        user_input: str = Field(description="The user input to be routed.")
        llm: Any = Field(description="The LLM to use for routing the user input.")
        router_prompt: SystemMessage = Field(description="The system prompt to use for routing the user input.")


    @tool(args_schema=SupervisorRouterInput)
    def supervisor_router(user_input, llm, router_prompt) -> str:
        """
        Routes the user input to the appropriate agent based on the content of the input.
        :param user_input: The user input to be routed.
        :param llm: The LLM to use for routing the user input.
        :param router_prompt: The system prompt to use for routing the user input.
        :return: The name of the agent to which the user input should be routed."""
        user_input = HumanMessage(
            content=f"{user_input}"
        )
        messages = [
            router_prompt,
            user_input
        ]
        response = llm.invoke(messages)
        if 'maximo' in response.content.lower():
            supervisor_decision = "maximo"
        elif 'vector_db' in response.content.lower():
            supervisor_decision = "vector_db"
        elif 'unknown' in response.content.lower():
            supervisor_decision = "unknown"

        supervisor_decision = response.content.lower()
        return supervisor_decision

    
    class SupervisorEvaluatorInput(BaseModel):
        user_input: str = Field(description="The user input.")
        agent_response: Any = Field(description="The response to be evaluated.")
        llm: Any = Field(description="The LLM to use for evaluation.")
        evaluation_prompt: SystemMessage = Field(description="The system prompt to use for evaluation.")


    @tool(args_schema=SupervisorEvaluatorInput)
    def supervisor_evaluation(user_input, agent_response, llm, evaluation_prompt) -> str:
        """
        Evaluates the agent response based on the user input and the evaluation prompt.
        :param user_input: The user input.
        :param agent_response: The response to be evaluated.
        :param llm: The LLM to use for evaluation.
        :param evaluation_prompt: The system prompt to use for evaluation.
        :return: The evaluation result."""
        user_input = HumanMessage(
            content=agent_response
        )
        messages = [
            evaluation_prompt,
            user_input
        ]
        result = llm.invoke(messages)
        # update the state with the evaluation result.
        final_response = result.content
        return final_response