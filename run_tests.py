import argparse

from tests.test_api import test_get_maximo_data, test_update_maximo_data 
from tests.test_llms import (
    test_generate_maximo_payload, 
    test_maximo_tool_use, 
    test_get_maximo_wo_details,
    test_maximo_supervisor_response
)
from dotenv import load_dotenv
_ = load_dotenv()

# Function map
FUNCTION_MAP = {
    "test_get_maximo_data": test_get_maximo_data,
    "test_generate_maximo_payload": test_generate_maximo_payload,
    "test_maximo_tool_use": test_maximo_tool_use,
    "test_get_maximo_wo_details": test_get_maximo_wo_details,
    "test_maximo_supervisor_response": test_maximo_supervisor_response,
    "test_update_maximo_data": test_update_maximo_data
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
    data = test_function()
else:
    # If no test name is provided, run all tests
    test_get_maximo_data()
    test_generate_maximo_payload()
    test_maximo_tool_use()
    test_get_maximo_wo_details()
    test_maximo_supervisor_response()
    test_update_maximo_data()
    print("All tests executed successfully.")
