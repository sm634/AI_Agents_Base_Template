import argparse
from dotenv import load_dotenv
_ = load_dotenv(override=True)

from tests.test_api import (
    test_postgres_create_table, 
    test_postgres_insert_data, 
    test_postgres_query_data,
    test_milvus_search,
    test_postgres_run_query,
    test_postgres_list_table_schemas,
    test_validate_with_pglast
)
from tests.test_llms import (
    test_postgres_agent_tools,
    test_vectordb_agent_tools,
)

from dotenv import load_dotenv
#from tools.report_generator_tools import generate_reports
_ = load_dotenv()
 
# Function map
FUNCTION_MAP = {
    "test_postgres_create_table": test_postgres_create_table,
    "test_postgres_insert_data": test_postgres_insert_data,
    "test_postgres_query_data": test_postgres_query_data,
    "test_postgres_agent_tools": test_postgres_agent_tools,
    "test_milvus_search": test_milvus_search,
    "test_vectordb_agent_tools": test_vectordb_agent_tools,
    "test_postgres_run_query": test_postgres_run_query,
    "test_postgres_list_table_schemas": test_postgres_list_table_schemas,
    "test_validate_with_pglast": test_validate_with_pglast,
}
# Parse command line arguments
parser = argparse.ArgumentParser(description="Run specific tests.")
parser.add_argument(
    "--function",
    choices=FUNCTION_MAP.keys(),
    help="Name of the test test function to run.",
)
args = parser.parse_args()
# Run the specified test function
if args.function:
    test_function = FUNCTION_MAP[args.function]
    if hasattr(test_function, 'invoke'):
        data = test_function.invoke({"query": 'SELECT * FROM "TEST"'})
    else:
        data = test_function()
    print(data)
    print("Test Successfully Completed!")
