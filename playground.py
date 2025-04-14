import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Set the path to your PDF file
pdf_path = "data/ventilation_doc.pdf"

# Load the PDF document
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# Split the document into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# Initialize the embedding model
embedding_function = HuggingFaceEmbeddings(model_name="ibm-granite/granite-embedding-30m-english")

# Set the directory for persistence
persist_directory = "./chroma_db"

# Create the Chroma vector store
vectordb = Chroma(
    collection_name="pdf_collection",
    embedding_function=embedding_function,
    persist_directory=persist_directory
)

# Add documents to the vector store
vectordb.add_documents(docs)


print(f"Successfully ingested {len(docs)} chunks into Chroma at '{persist_directory}'.")

# breakpoint()

# Load the persisted Chroma vector store
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding_function
)

# Define your search query
query = "What are some issues with noise on a ventilation system?"

# Perform a similarity search
results = vectordb.similarity_search(query, k=4)

# Display the search results
for idx, doc in enumerate(results, start=1):
    print(f"Result {idx}:")
    print(doc.page_content)
    print("-" * 80)

breakpoint()