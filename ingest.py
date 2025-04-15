from connectors.vector_db_connector import ChromaDB

def ingest_documents():
    client = ChromaDB()
    client.ingest_documents()

if __name__ == "__main__":
    ingest_documents()
