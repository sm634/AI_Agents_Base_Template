import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from connectors.db_connector import PostgresConnector
from pydantic import BaseModel, Field
from typing import Dict, Union, Any
from langchain.agents import tool
from langchain_core.messages import HumanMessage, SystemMessage

class PostGresAgentTools:

    class GenerateSQLQuery(BaseModel):
        user_input: str = Field(description="The user input to be translated to sql query to run.")
        system_prompt: Any = Field(description="The prompt to be used to help the LLM generate the sql query to run.")
        llm: Any = Field(description="The LLM to use for generating the SQL query.")

    @tool(args_schema=GenerateSQLQuery)
    def generate_query(user_input: str, system_prompt: str, llm: Any) -> Dict[str, Any]:
            """
            Generates the SQL query based on the user input.
            :param user_input: The user_input.
            :param system_prompt: The system prompt to use for generating the SQL query.
            :param llm: The LLM to use for generating the SQL query.
            :return: A dictionary containing the SQL query.
            """

            user_input = HumanMessage(
                content=user_input
            )
            messages = [
                system_prompt,
                user_input,
            ]

            response = llm.invoke(messages)
            query = response.content

            return query


    class QueryInput(BaseModel):
        query: str = Field(description="The SQL query for postgres to run.")
        params: Any = Field(description="The parameters for the query to configure it/optimise it.")

    @tool(args_schema=QueryInput)
    def run_query(query: str, params=None):
        """
        A tool to generate sql query based on user input and run that query on the postgres database.
        :user_input: the user input to be translated to sql query to run.
        :system_prompt: the prompt to be used to help the LLM generate the sql query to run.
        :llm: the LLM to use for generating the SQL query.
        :return: The output of the SQL query.
        """
        # Generate the SQL query using the LLM
        try:
            # Generate the SQL query using the LLM
            pg_connector = PostgresConnector()
            response = pg_connector.run_query(query=query, params=params)

        except Exception as e:
            response = {
                "status": "error",
                "error": str(e)
            }
        
        return response
    
    class GetTableSchemas(BaseModel):
        table_name: str = Field(description="The name of the table to get the schema for.")
        params: Any = Field(description="The parameters for the query to configure it/optimise it.")
        
    @tool(args_schema=GetTableSchemas)
    def get_table_schemas(self, table_name: str) -> Dict[str, Any]:
        """
        Get the schema of a table in the database.
        :param table_name: The name of the table to get the schema for.
        :return: A dictionary containing the schema of the table.
        """
        pg_connector = PostgresConnector()
        response = pg_connector.get_table_schemas(table_name=table_name)
        return response
    
    class validate_sql_query(BaseModel):
        query: str = Field(description="The SQL query to validate.")
        params: Any = Field(description="The parameters for the query to configure it/optimise it.")
        
    @tool(args_schema=validate_sql_query)
    def validate_sql_query(query: str, params=None) -> Dict[str, Any]:
        """
        Validate the SQL query.
        :param query: The SQL query to validate.
        :param params: The parameters for the query to configure it/optimise it.
        :return: A dictionary containing the validation result.
        """
        pg_connector = PostgresConnector()
        response = pg_connector.validate_with_pglast_Latest(query=query, params=params)
        return response
    
    class validate_sql_query(BaseModel):
        query: str = Field(description="The SQL query to validate.")
        params: Any = Field(description="The parameters for the query to configure it/optimise it.")
    @tool(args_schema=validate_sql_query)
    def validate_sql_query(query: str, params=None) -> Dict[str, Any]:
        """
        Validate the SQL query.
        :param query: The SQL query to validate.
        :param params: The parameters for the query to configure it/optimise it.
        :return: A dictionary containing the validation result.
        """
        pg_connector = PostgresConnector()
        response = pg_connector.validate_with_pglast_Latest(query=query, params=params)
        return response