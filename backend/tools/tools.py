from typing import Annotated
import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

import subprocess
import ibm_db
import pandas as pd
import datetime
import ibm_boto3
from ibm_botocore.client import Config

tavily_tool = TavilySearchResults(max_results=5)

# This executes code locally, which can be unsafe
repl = PythonREPL()


@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code and do math. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n\`\`\`python\n{code}\n\`\`\`\nStdout: {result}"
    return result_str


@tool
def connect_to_maximo_db2(hostname, port, database, user, password):
    try:
        conn_str = f'DATABASE={database};HOSTNAME={hostname};PORT={port};UID={user};PWD={password};'
        connection = ibm_db.connect(conn_str, '', '')
        if connection:
            print("Connection to DB2 Maximo database successful!")
            return connection
        else:
            print("Failed to connect to DB2 database.")
            return None
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

@tool
def fetch_asset_data(connection):
    try:
        ibm_db.exec_immediate(connection, "SET CURRENT SCHEMA = 'MAXIMO'")
        sql = """
            SELECT 
                a.assetnum, a.parent, a.serialnum, a.priority, a.description AS asset_description, 
                a.status, a.failurecode, a.manufacturer,
                am.metername, am.readingtype, am.lastreading, am.LASTREADINGDATE,
                l.location, l.description AS location_description
            FROM asset a
            LEFT JOIN assetmeter am ON a.assetnum = am.assetnum AND a.siteid = am.siteid
            LEFT JOIN locations l ON a.location = l.location AND a.siteid = l.siteid
            ORDER BY a.assetnum, am.metername;
        """
        
        stmt = ibm_db.exec_immediate(connection, sql)
        rows = []
        row = ibm_db.fetch_assoc(stmt)
        while row:
            rows.append(row)
            row = ibm_db.fetch_assoc(stmt)

        print(f"Fetched {len(rows)} records from asset.")
        return rows

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@tool
def export_to_csv(data, output_file):
    try:
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
            print(f"Data exported successfully to {output_file}!")
        else:
            print("No data to export.")
    except Exception as e:
        print(f"Error exporting data to CSV: {e}")


@tool
def upload_file_to_cos(bucket_name, exported_file_name):
    try:
        cos = ibm_boto3.resource(
            "s3",
            ibm_api_key_id=os.environ['COS_API_KEY_ID'],
            ibm_service_instance_id=os.environ['COS_SERVICE_CRN'],
            config=Config(signature_version="oauth"),
            endpoint_url=os.environ['COS_ENDPOINT']
        )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"asset_{timestamp}.csv"
        cos.Bucket(bucket_name).upload_file(exported_file_name, file_name)
        print(f"File '{file_name}' uploaded successfully to bucket '{bucket_name}'!")
    except Exception as e:
        print(f"Failed to upload file to COS: {e}")
