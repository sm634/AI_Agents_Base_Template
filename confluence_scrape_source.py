from langchain_community.document_loaders import ConfluenceLoader, PyPDFLoader
from langchain_milvus import Milvus
# from langchain_milvus import Milvus
from pymilvus import connections, Collection, FieldSchema, DataType, CollectionSchema
import numpy as np
from uuid import uuid4
from langchain_ibm.embeddings import WatsonxEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()


# scrape data from confluence
loader = ConfluenceLoader(
    url=os.getenv("url"),
    username=os.getenv("username"),
    api_key=os.getenv("api_key"),
    space_key=os.getenv("space_key"),
    include_attachments=True,
    limit=50
)
documents = loader.load()

# chunking of data
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
uuids = [str(uuid4()) for _ in range(len(texts))]
# embeddings the text
embeddings = WatsonxEmbeddings(
    model_id="ibm/slate-125m-english-rtrvr",
    url=os.environ['WATSONX_URL'],
    project_id=os.environ["WATSONX_PROJECT_ID"],
    apikey=os.environ['WATSONX_APIKEY']
)


# Now initialize the vector store with LangChain Milvus
vector_store = Milvus(
    collection_name="DevOpsAssist",    
    embedding_function=embeddings,
    connection_args={
        "uri": f"grpc://{os.environ['grpcHost']}:{os.environ['grpcPort']}",
        "user": os.environ['milvusUser'],  # Ensure "user" is used instead of "username"
        "password": os.environ['milvusPass'],
        "secure": True  # Set to True if Watsonx requires TLS
    },
    index_params={"index_type": "FLAT", "metric_type": "L2"},
    consistency_level="Strong",
    drop_old=True
)

print("✅ Successfully connected to Milvus!")

print("Adding documents to Milvus instance.")
vector_store.add_documents(documents=texts, ids=uuids)
print("✅ Documents successfully added")
