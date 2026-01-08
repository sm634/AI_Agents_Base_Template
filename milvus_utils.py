from langchain_milvus import Milvus
from langchain_ibm.embeddings import WatsonxEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

def get_embedding_model():
    return WatsonxEmbeddings(
        model_id="ibm/slate-125m-english-rtrvr",
        url=os.environ['WATSONX_URL'],
        project_id=os.environ["WATSONX_PROJECT_ID"],
        apikey=os.environ['WATSONX_APIKEY']
    )

def get_vector_store(drop_old=False):
    embeddings = get_embedding_model()
    return Milvus(
        collection_name="DevOpsAssist",
        embedding_function=embeddings,
        connection_args={
            "uri": f"grpc://{os.environ['grpcHost']}:{os.environ['grpcPort']}",
            "user": os.environ['milvusUser'],
            "password": os.environ['milvusPass'],
            "secure": True
        },
        index_params={"index_type": "FLAT", "metric_type": "L2"},
        consistency_level="Strong",
        drop_old=drop_old
    )
