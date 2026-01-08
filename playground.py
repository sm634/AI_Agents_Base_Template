import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from datetime import datetime
from connectors.db_connector import PostgresConnector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic import BaseModel, Field
from langchain.tools import tool
from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Union, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os
import base64
load_dotenv()
# Sample DataFrame
# data = {
#     'feedback_id': [1, 2, 3],
#     'user': ['anonymous', 'anonymous', 'anonymous'],
#     'feedback': ['Test1', 'The application is amazing! I will use it to help me from now on.', 'Testing on the feedback widget'],
#     'timestamp': [datetime(2025, 6, 9, 12, 22, 24, 208032), datetime(2025, 6, 9, 13, 0, 5, 728378), datetime(2025, 6, 10, 13, 56, 36, 668538)]
# }

# df = pd.DataFrame(data)

# Hypothetical LLM invoke function
# def llm_invoke(prompt):
#     # This is a placeholder for the actual LLM invocation
#     # In a real scenario, this would call the LLM API and return the generated text
#     return f"Generated text based on prompt: {prompt}"

# # Function to generate summary report from DataFrame using LLM
# def generate_summary_report_with_llm(df, file_path):
#     # Generate the introduction
#     intro_prompt = "Generate an introduction for a summary report on the benefits of DevOps Chat Assist."
#     introduction = llm_invoke(intro_prompt)

#     # Generate the key insights
#     insights_prompt = "Summarize the following DataFrame:\n" + df.to_string(index=False)
#     key_insights = llm_invoke(insights_prompt)

#     # Generate the business implications
#     implications_prompt = "Provide business implications based on the following key insights:\n" + key_insights
#     business_implications = llm_invoke(implications_prompt)

#     # Generate the recommendations
#     recommendations_prompt = "Provide recommendations based on the following key insights:\n" + key_insights
#     recommendations = llm_invoke(recommendations_prompt)

#     # Generate the conclusion
#     conclusion_prompt = "Generate a conclusion for the summary report based on the following key insights, business implications, and recommendations:\n" + key_insights + "\n" + business_implications + "\n" + recommendations
#     conclusion = llm_invoke(conclusion_prompt)

#     # Combine all sections to form the complete summary report
#     summary_report = f"""
#     ### Summary Report

#     #### Introduction

#     {introduction}

#     #### Key Insights

#     {key_insights}

#     #### Business Implications

#     {business_implications}

#     #### Recommendations

#     {recommendations}

#     #### Conclusion

#     {conclusion}
#     """

#     # Write the summary report to the file
#     with open(file_path, 'w') as f:
#         f.write(summary_report)

# # Specify the file path where you want to save the summary report
# file_path = 'summary_report.txt'

# # Generate the summary report using LLM
# generate_summary_report_with_llm(df, file_path)

# print(f"Summary report has been generated and saved to {file_path}")

# # Function to generate summary report from DataFrame using LLM
# def generate_summary_report_with_llm(df):
#     """
#     Generate a summary report from a DataFrame using LLM.

#     Args:
#     - df (pd.DataFrame): The input DataFrame.

#     Returns:
#     - str: The generated summary report.
#     """

#     # Get the shape of the DataFrame
#     num_rows, num_cols = df.shape

#     # Get the column names and data types
#     column_info = ', '.join([f'{col}: {df[col].dtype}' for col in df.columns])

#     # Get the summary statistics of the DataFrame
#     summary_stats = df.describe().to_string()

#     # Get the distribution of values in categorical columns
#     categorical_cols = df.select_dtypes(include=['object']).columns
#     categorical_dist = {col: df[col].value_counts().to_string() for col in categorical_cols}

#     # Get the correlation between numerical columns
#     numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
#     correlation_matrix = df[numerical_cols].corr().to_string()

#     # Create a prompt for the LLM
#     prompt = f"""
#     Generate a summary report for a DataFrame with {num_rows} rows and {num_cols} columns.
#     The columns are: {column_info}.
#     The summary statistics are: {summary_stats}.
#     The distribution of values in categorical columns are: {categorical_dist}.
#     The correlation between numerical columns is: {correlation_matrix}.
#     The data contains feedback information with a timestamp.
#     """

#     # Invoke the LLM to generate the summary report
#     summary_report = llm_invoke(prompt)

#     return summary_report
# summary_report = generate_summary_report_with_llm(df)
# print(summary_report)
# class ReportGenerator(ABC):
#     @abstractmethod
#     def generate_report(self, df):
#         pass
# class SummaryReportGenerator(ReportGenerator):
#     def generate_report(self, df, output_file='reports/summary_report.html'):
#         with open(output_file, 'w') as f:
#             # Introduction
#             f.write("<p>DevOps Chat Assist represents a significant advancement in DevOps tooling, offering a range of features and benefits that can greatly enhance the efficiency, collaboration, and reliability of DevOps teams. By leveraging this tool, organizations can achieve faster time to market, reduced costs, and improved customer satisfaction.</p><br/>")

#             # Key Insights
#             f.write("<h2><u><i>Key Insights</i></u></h2>")
#             f.write("<p>The analysis of the dataset reveals several key insights that can inform business decisions. These include:</p>")

#             # Generate key insights using LLM
#             insights_prompt = "Summarize the following DataFrame:\n" + df.to_string(index=False)
#             key_insights = self.llm_invoke(insights_prompt)

#             f.write("<p>{}</p>".format(key_insights))

#             f.write("<table border='1'>")
#             f.write("<tr><th>Row</th>")
#             for column in df.columns:
#                 f.write("<th>{}</th>".format(column))
#             f.write("</tr>")
#             for index, row in df.iterrows():
#                 f.write("<tr><td>{}</td>".format(index))
#                 for value in row:
#                     f.write("<td>{}</td>".format(value))
#                 f.write("</tr>")
#             f.write("</table><br/>")

#             # Business Implications
#             f.write("<h2><u><i>Business Implications</i></u></h2>")
#             f.write("<p>The insights gained from this analysis have significant implications for the business. By leveraging DevOps Chat Assist, organizations can:</p>")
#             f.write("<ul>")
#             f.write("<li>Improve collaboration and communication among team members, leading to faster time to market and reduced costs.</li>")
#             f.write("<li>Enhance the reliability and efficiency of DevOps processes, resulting in improved customer satisfaction.</li>")
#             f.write("</ul><br/>")

#             # Recommendations
#             f.write("<h2><u><i>Recommendations</i></u></h2>")
#             f.write("<p>Based on the findings of this analysis, we recommend that organizations:</p>")
#             f.write("<ul>")
#             f.write("<li>Implement DevOps Chat Assist to streamline DevOps processes and improve collaboration.</li>")
#             f.write("<li>Continuously monitor and analyze key metrics to identify areas for improvement and optimize DevOps processes.</li>")
#             f.write("</ul><br/>")

#             # Conclusion
#             f.write("<h1><u><i>Conclusion</i></u></h1>")
#             f.write("<p>In conclusion, DevOps Chat Assist offers a range of benefits that can enhance the efficiency, collaboration, and reliability of DevOps teams. By leveraging this tool and following the recommendations outlined in this report, organizations can achieve significant improvements in their DevOps processes.</p>")
#             f.write("</body></html>")
                

#     def llm_invoke(self, prompt):
#         # This is a placeholder for the actual LLM invocation
#         # In a real scenario, this would call the LLM API and return the generated text
#         return f"Generated text based on prompt: {prompt}"

# # Assuming your DataFrame is named df and the class is defined as in your code

# # Create an instance of the summary report generator
# summary_generator = SummaryReportGenerator()

# # Generate the summary report HTML file
# summary_generator.generate_report(df, output_file='summary_report.html')

# print("Summary report has been generated and saved to summary_report.html")

class DataFetcher:
    def __init__(self, connector):
        self.connector = connector

    def fetch_data(self, query):
        data = self.connector.query_data(query=query)
        cols = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=cols)
        self.connector.close_connection()
        return df
def generate_markdown_summary_report(df):
    import pandas as pd

    # Column Overview
    column_overview = "| Column Name | Data Type |\n|---|---|\n"
    for col in df.columns:
        column_overview += f"| {col} | {df[col].dtype} |\n"

    # Summary Statistics
    summary_stats = df.describe(include='all').T
    summary_stats_md = summary_stats.reset_index().to_markdown(index=False)

    # Categorical Distributions
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    categorical_md = ""
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        categorical_md += f"\n**{col}**\n\n"
        categorical_md += value_counts.reset_index().rename(
            columns={'index': col, col: 'Count'}
        ).to_markdown(index=False)
        categorical_md += "\n"

    # Correlations
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 1:
        corr_md = df[numerical_cols].corr().to_markdown()
    elif len(numerical_cols) == 1:
        corr_md = f"| {numerical_cols[0]} |\n|---|\n| 1.0 |"
    else:
        corr_md = "No numerical columns to correlate."

    # Timestamps
    time_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    time_trend_md = ""
    if len(time_cols) > 0:
        for col in time_cols:
            min_time = df[col].min()
            max_time = df[col].max()
            time_trend_md += f"- **{col}** ranges from `{min_time}` to `{max_time}`.\n"
        # Example: show counts per day if available
        time_col = time_cols[0]
        time_counts = df[time_col].dt.date.value_counts().sort_index()
        time_trend_md += "\n**Entries per day:**\n\n"
        time_trend_md += time_counts.reset_index().rename(
            columns={'index': 'Date', time_col: 'Count'}
        ).to_markdown(index=False)
    else:
        time_trend_md = "No timestamp columns found."

    # Combine all sections
    report = f"""
### Column Overview

{column_overview}

### Summary Statistics

{summary_stats_md}

### Categorical Distributions

{categorical_md}

### Correlations

{corr_md}

### Timestamps

{time_trend_md}
"""
    return report

# Example usage:
# print(generate_markdown_summary_report(df))
def save_markdown_summary_report(df, output_file="summary_report.md"):
    import pandas as pd

    # Column Overview
    column_overview = "| Column Name | Data Type |\n|---|---|\n"
    for col in df.columns:
        column_overview += f"| {col} | {df[col].dtype} |\n"

    # Summary Statistics
    summary_stats = df.describe(include='all').T
    summary_stats_md = summary_stats.reset_index().to_markdown(index=False)

    # Categorical Distributions
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    categorical_md = ""
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        categorical_md += f"\n**{col}**\n\n"
        categorical_md += value_counts.reset_index().rename(
            columns={'index': col, col: 'Count'}
        ).to_markdown(index=False)
        categorical_md += "\n"

    # Correlations
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 1:
        corr_md = df[numerical_cols].corr().to_markdown()
    elif len(numerical_cols) == 1:
        corr_md = f"| {numerical_cols[0]} |\n|---|\n| 1.0 |"
    else:
        corr_md = "No numerical columns to correlate."

    # Timestamps
    time_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    time_trend_md = ""
    if len(time_cols) > 0:
        for col in time_cols:
            min_time = df[col].min()
            max_time = df[col].max()
            time_trend_md += f"- **{col}** ranges from `{min_time}` to `{max_time}`.\n"
        # Example: show counts per day if available
        time_col = time_cols[0]
        time_counts = df[time_col].dt.date.value_counts().sort_index()
        time_trend_md += "\n**Entries per day:**\n\n"
        time_trend_md += time_counts.reset_index().rename(
            columns={'index': 'Date', time_col: 'Count'}
        ).to_markdown(index=False)
    else:
        time_trend_md = "No timestamp columns found."

    # Combine all sections
    report = f"""
### Column Overview

{column_overview}

### Summary Statistics

{summary_stats_md}

### Categorical Distributions

{categorical_md}

### Correlations

{corr_md}

### Timestamps

{time_trend_md}
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

# Example usage:
# save_markdown_summary_report(df, "summary_report.md")

# 1. Connect to your JIRA-Data database
connector = PostgresConnector(
    dbname="JIRA-Data",
    user="your_user",
    password="your_password",
    host="your_host",
    port="your_port"
)

# 2. Fetch data from the desired table (e.g., jira_data)
fetcher = DataFetcher(connector)
df = fetcher.fetch_data("SELECT * FROM jira_data")

# 3. Generate and print the Markdown summary report
print(generate_markdown_summary_report(df))

# 4. Optionally, save the report to a file
save_markdown_summary_report(df, "jira_summary_report.md")
