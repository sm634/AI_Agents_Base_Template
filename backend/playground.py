# Required Libraries
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_ibm import WatsonxLLM
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


# -----------------------------
# Define Agent State Schema
# -----------------------------
class AgentState(BaseModel):
    user_input: str
    supervisor_decision: Optional[str] = None
    milvus_result: Optional[str] = None
    memory_chain: List[Dict[str, Any]] = []


# -----------------------------
# Milvus Query Tool
# -----------------------------
class MilvusClient:
    def __init__(self, collection_name: str):
        self.collection = Collection(name=collection_name)

    def query(self, text: str) -> str:
        # You'd use an embedding model and query Milvus here
        # This is a mock result for demonstration
        return f"[Milvus search result for: '{text}']"


# -----------------------------
# Milvus Agent
# -----------------------------
class MilvusAgent:
    def __init__(self, llm, milvus_client: MilvusClient):
        self.llm = llm
        self.client = milvus_client

    def run(self, state: AgentState) -> AgentState:
        query = state.user_input
        result = self.client.query(query)
        return state.copy(update={"milvus_result": result})


# -----------------------------
# Supervisor Agent
# -----------------------------
class SupervisorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a router. Classify the user's query as 'milvus' or 'unknown'."),
            ("human", "{query}")
        ])

    def classify_query(self, user_input: str) -> str:
        messages = self.classification_prompt.format_messages(query=user_input)
        response = self.llm.invoke(messages)
        return response.content.strip().lower()

    def handle_input(self, state: AgentState) -> AgentState:
        decision = self.classify_query(state.user_input)
        state.memory_chain.append({
            "input": state.user_input,
            "decision": decision,
            "output": "PENDING"
        })
        return state.copy(update={"supervisor_decision": decision})

    def postprocess(self, state: AgentState) -> AgentState:
        result = state.milvus_result or "No result."
        state.memory_chain[-1]["output"] = result
        return state


# -----------------------------
# Routing Function
# -----------------------------
def supervisor_router(state: AgentState) -> str:
    if state.supervisor_decision == "milvus":
        return "milvus_agent"
    else:
        return "supervisor_postprocess"


# -----------------------------
# Build the Graph
# -----------------------------
def build_graph(llm, milvus_client):
    graph = StateGraph(AgentState)

    supervisor = SupervisorAgent(llm=llm)
    milvus_agent = MilvusAgent(llm=llm, milvus_client=milvus_client)

    graph.add_node("supervisor", supervisor.handle_input)
    graph.add_node("milvus_agent", milvus_agent.run)
    graph.add_node("supervisor_postprocess", supervisor.postprocess)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", supervisor_router)
    graph.add_edge("milvus_agent", "supervisor_postprocess")
    graph.set_finish_point("supervisor_postprocess")

    return graph.compile()


# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    import os
    from pymilvus import connections

    # Connect to Milvus
    connections.connect(alias="default", host="localhost", port="19530")

    # Set up LLM
    llm = WatsonxLLM(
        model_id="ibm/granite-13b-chat-v2",
        url=os.environ["WATSONX_URL"],
        apikey=os.environ["IBM_CLOUD_APIKEY"],
        project_id=os.environ["WATSONX_PROJECT_ID"]
    )

    # Initialize graph
    milvus_client = MilvusClient(collection_name="my_collection")
    graph = build_graph(llm, milvus_client)

    # Run
    state = AgentState(user_input="Find documents about vector databases")
    result = graph.invoke(state)

    print("Final result:")
    print(result.model_dump())



from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph

tool_executor = ToolExecutor([maximo_operation])

def maximo_agent_step(state: AgentState) -> AgentState:
    messages = [
        SystemMessage(content=...),
        HumanMessage(content=state.user_input)
    ]

    # Step 1: Get the LLM response (might be tool call)
    result = llm.invoke(messages)

    # Step 2: If it's a tool call, execute it
    if isinstance(result, dict) and 'tool_calls' in result:
        for tool_call in result['tool_calls']:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            # You can either use LangChain's tool execution logic
            # or just call your function directly
            if tool_name == "maximo_operation":
                output = maximo_operation(**tool_args)
                # Add to state or return directly
                return {**state, "output": output}
    else:
        return {**state, "output": result.content}
