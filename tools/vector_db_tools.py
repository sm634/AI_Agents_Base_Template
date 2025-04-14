from connectors.vector_db_connector import ChromaDB

from pydantic import BaseModel, Field
from typing import Dict, Union
from langchain.agents import tool


class VectorAgentTools:

    class SearchInput(BaseModel):
        user_input: Union[Dict, str] = Field(description="The payload to be sent to Maximo.")

    @tool(args_schema=SearchInput)
    def search(user_input: str):
        """
        Perform search on a vector db.
        :user_input: the query to search in the vector db.
        :return: List of search results.
        """

        vector_db = ChromaDB()
        response = vector_db.search(query=user_input)
        results = [doc.page_content for doc in response]
        return results
