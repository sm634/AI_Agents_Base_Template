## Root: agentic-query-router

# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
POSTGRES_URI = os.getenv("POSTGRES_URI")
S3_BUCKET = os.getenv("S3_BUCKET")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# app/data_sources.py
from langchain.vectorstores import Milvus
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.utilities import SQLDatabase
from langchain.document_loaders import S3FileLoader
import boto3
from .config import *

embedding_fn = HuggingFaceEmbeddings(model_name="ibm-granite/base.en")

milvus_vectorstore = Milvus(
    collection_name="granite_collection",
    connection_args={"host": MILVUS_HOST, "port": "19530"},
    embedding_function=embedding_fn
)

postgres_db = SQLDatabase.from_uri(POSTGRES_URI)

s3_loader = S3FileLoader(bucket=S3_BUCKET, prefix="documents/")
docs = s3_loader.load()

# app/retrievers.py
from langchain.chains import SQLDatabaseChain, RetrievalQA
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.chat_models import ChatOpenAI
from .data_sources import milvus_vectorstore, postgres_db, docs, embedding_fn

llm = ChatOpenAI(temperature=0)

retrievers = {
    "milvus": RetrievalQA.from_chain_type(llm=llm, retriever=milvus_vectorstore.as_retriever()),
    "postgres": SQLDatabaseChain.from_llm(llm, db=postgres_db),
    "s3": RetrievalQA.from_chain_type(
        llm=llm,
        retriever=VectorStoreRetriever.from_documents(docs, embedding_fn)
    )
}

# app/router.py
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0)

router_template = """
You are a smart router deciding which data source is best to answer the following question.
Available tools are:
- "milvus": for semantic or unstructured queries.
- "postgres": for structured data or analytics.
- "s3": for document-based queries.

Question: {input}
Respond with one word: "milvus", "postgres", or "s3".
"""

router_prompt = PromptTemplate.from_template(router_template)
router_chain = LLMChain(llm=llm, prompt=router_prompt)

def llm_router(query: str) -> str:
    response = router_chain.run(input=query).strip().lower()
    return response if response in ["milvus", "postgres", "s3"] else "milvus"

# app/main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from .router import llm_router
from .retrievers import retrievers

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(req: QueryRequest):
    destination = llm_router(req.query)
    result = retrievers[destination].run(req.query)
    return {"destination": destination, "response": result}

# ui/package.json (React boilerplate assumed)
# Create React App or Vite with Tailwind or MUI suggested

# # .env (example)
# MILVUS_HOST=localhost
# POSTGRES_URI=postgresql://user:password@host:5432/dbname
# S3_BUCKET=your-bucket
# HUGGINGFACE_API_KEY=your-key

# # requirements.txt
# langchain
# langgraph
# openai
# psycopg2
# boto3
# python-dotenv
# pymilvus
# huggingface_hub
# fastapi
# uvicorn

# # README.md (summarized)
# ## Agentic Query Router

# This app routes natural language questions to the correct data source (Milvus, Postgres, S3) using an LLM-based router and LangChain agents.

# ### Start Backend
# ```bash
# uvicorn app.main:app --reload
# ```

# ### Start Frontend
# ```bash
# cd ui
# npm install
# npm run dev
# ```

# ---

# Let me know if you want the full React frontend template too!
