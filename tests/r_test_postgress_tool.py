import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.postgres_agent_tools import PostGresAgentTools
from connectors.db_connector import PostgresConnector   

def test_postgres_tool():
    # Import the PostgresConnector class here to avoid circular import issues
    # Create an instance of the PostgresConnector
    pg_connector = PostgresConnector()

    # Test the connection
    assert pg_connector.conn is not None, "PostgreSQL connection failed"

    # Test getting table schemas
    schemas = pg_connector.get_table_schemas("jira_data")
    print(schemas)

    assert isinstance(schemas, list), "Failed to get table schemas"
