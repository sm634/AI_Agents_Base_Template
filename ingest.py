import argparse
from langchain_community.document_loaders import ConfluenceLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from uuid import uuid4
from connectors.vector_db_connector import MilvusConnector
import os


# Function map
FUNCTION_MAP = {
    "text_file": "Load text documents from a local directory",
    "confluence": "Load documents from Confluence"
}

# Parse command line arguments
parser = argparse.ArgumentParser(description="Ingest from different data sources.")
parser.add_argument(
    "--source",
    choices=FUNCTION_MAP.keys(),
    default="text_file",
    help="The source of the documents to ingest. Choose 'text_file' or 'confluence'.",
)
args = parser.parse_args()
# Run the specified test function
if args.source == 'text_file':
    # Load text documents from a local directory
    loader = TextLoader(
        file_path='data/FCC 6.3.0.0 Support Matrix.txt',
        encoding="utf-8"
    )
    documents = loader.load()

elif args.source == 'confluence':
    loader = ConfluenceLoader(
        url=os.getenv("confluenceURL"),
        username=os.getenv("confluenceUSERNAME"),
        api_key=os.getenv("confluence_APIKEY"),
        space_key=os.getenv("confluence_SPACEKEY"),
        include_attachments=True,
        limit=50
    )
    documents = loader.load()

connector = MilvusConnector()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
texts = text_splitter.split_documents(documents)
uuids = [str(uuid4()) for _ in texts]


vector_store = connector.get_vector_store(drop_old=True)
vector_store.add_documents(documents=texts, ids=uuids)
print("✅ Documents successfully added")