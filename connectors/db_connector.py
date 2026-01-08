import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from pglast import parse_sql, Error
from typing import Dict, Union, Any
import os
import re

class PostgresConnector:
    def __init__(self):
        """
        Initialize the PostgresConnector class.
        Establishes a connection to the PostgreSQL database.
        """
        try:
            self.conn = psycopg.connect(
                dbname=os.environ['PostGresDB'],
                user=os.environ['PostGresUser'],
                password=os.environ['PostGresPass'],
                host=os.environ['PostGresHost'],
                port=os.environ['PostGresPort'],
                connect_timeout=10
            )
            self.conn.autocommit = True  # Optional: Set autocommit mode
            print("Connection to PostgreSQL database established successfully.")
        except psycopg.Error as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            raise
        
    def get_table_schemas(self) -> Dict[str, Any]:
        """
        Get the schemas of all tables in the PostgreSQL database.
        """  
        with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name, column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position;
                """)
                results = cur.fetchall()
        schemas_text = ""
        current_table = None
        for row in results:
            table, column, data_type = row
            if current_table != table:
                if current_table is not None:
                    schemas_text += "\n"
                schemas_text += f"Table: {table}\n"
                current_table = table
            schemas_text += f"  Column: {column}, Type: {data_type}\n"
        return schemas_text
    
        #return results

    def create_table(self, table_name, schema):
        """
        Create a sample table with specified name.
        """
        create_table_query = sql.SQL("""CREATE TABLE IF NOT EXISTS {}""").format(sql.Identifier(table_name)) + sql.SQL(schema)

        with self.conn.cursor() as cur:
            cur.execute(create_table_query)
            print(f"Table '{table_name}' created or already exists.")

    def insert_data(self, table_name, data: dict):
        """
        Insert a single row into the specified table.
        `data` should be a dictionary where keys are column names and values are the values to insert.
        """
        columns = data.keys()
        values = data.values()

        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        with self.conn.cursor() as cur:
            cur.execute(insert_query, list(values))
            print(f"Inserted data into '{table_name}': {data}")


    def query_data(self, query, params=None):
        """
        Execute a custom SQL query and return the results.
        `query` should be a string or a psycopg.sql.SQL object.
        `params` is an optional tuple or list of parameters to bind to the query.
        """
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            output = [cols] + rows
            return output


    def close_connection(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            print("PostgreSQL database connection closed.")


    def run_query(self, query, params=None):
        """
        Run a SQL query on the PostgreSQL database.
        :param query: The SQL query to execute.
        :param params: Optional parameters for the query.
        :return: A dictionary containing the status and result of the query.
        """
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, params or ())
                    
                    if cur.description:  # SELECT or RETURNING queries
                        rows = cur.fetchall()
                        return {"status": "ok", "type": "select", "data": rows}
                    else:  # INSERT, UPDATE, DELETE
                        self.conn.commit()
                        return {"status": "ok", "type": "write", "rowcount": cur.rowcount}
                        
        except Exception as e:
            return {"status": "error", "error": str(e)}
        
    
    def list_table_schemas(self):
        """
        List all tables and their schemas in the database.
        """
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """)

            # Fetch all results
            results = cur.fetchall()

            # Format the results
            formatted_results = {}
            for row in results:
                table_name = row['table_name']
                column_name = row['column_name']
                data_type = row['data_type']

                if table_name not in formatted_results:
                    formatted_results[table_name] = []

                formatted_results[table_name].append({
                    'column_name': column_name,
                    'data_type': data_type
                })

            return results
    

    def validate_with_pglast(self, sql: str) -> bool:
        """
        Validate SQL syntax using pglast.
        :param sql: The SQL query to validate.
        :return: True if valid, False otherwise.
        """
        # Check if the SQL query is empty
        try:
            parse_sql(sql)
            return True
        except Error as e:
            print("Syntax error:", e)
            return False
        
    @staticmethod
    def validate_with_pglast_Latest(sql: str):
        """
        Validate SQL syntax using pglast.
        Returns a dict with 'valid': bool and 'error': str (if any).
        """
        try:
            parse_sql(sql)
            return {"valid": True, "error": None}
        except Error as e:
            return {"valid": False, "error": str(e)}