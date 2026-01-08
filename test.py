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
connector = PostgresConnector()


def generate_markdown_summary_report(df):

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
connector = PostgresConnector()
# 2. Fetch data from the desired table (e.g., jira_data)
fetcher = DataFetcher(connector)
df = fetcher.fetch_data("SELECT \"Status\", COUNT(*) FROM jira_data GROUP BY \"Status\"")

# 3. Generate the Markdown summary report and save to a text file
report_text = generate_markdown_summary_report(df)

# Add a title and horizontal rules for better readability
formatted_report = f"""\
#############################################################
#                    JIRA Data Summary Report               #
#############################################################

This report provides a concise overview and statistics for the JIRA data.

---

{report_text}

---
"""

with open("jira_summary_report.txt", "w", encoding="utf-8") as f:
    f.write(formatted_report)

# 4. Optionally, also save the report as markdown
save_markdown_summary_report(df, "jira_summary_report.md")
def save_html_summary_report(df, output_file="jira_summary_report.html"):
    # CSS styles for tables and headers
    css = """
    <style>
    body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
    h1, h2, h3 { color: #2c3e50; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }
    th, td { border: 1px solid #bbb; padding: 8px 12px; text-align: left; }
    th { background: #2c3e50; color: #fff; }
    tr:nth-child(even) { background: #f2f2f2; }
    code { background: #eee; padding: 2px 4px; border-radius: 4px; }
    .section { margin-bottom: 40px; }
    </style>
    """

    # Generate markdown sections as HTML
    def md_table_to_html(md_table):
        import pandas as pd
        lines = [line for line in md_table.strip().split('\n') if line.strip()]
        # Find header and separator
        header_idx = None
        for i, line in enumerate(lines):
            if line.startswith('|') and line.endswith('|'):
                header_idx = i
                break
        if header_idx is None or header_idx + 1 >= len(lines):
            return f"<pre>{md_table}</pre>"
        header = [h.strip() for h in lines[header_idx].split('|')[1:-1]]
        # Find where the separator row is (usually right after header)
        sep_idx = header_idx + 1
        # Data rows start after separator
        data_rows = []
        for line in lines[sep_idx+1:]:
            if not line.startswith('|'):
                continue
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            # Pad or trim row to match header length
            if len(row) < len(header):
                row += [''] * (len(header) - len(row))
            elif len(row) > len(header):
                row = row[:len(header)]
            data_rows.append(row)
        df = pd.DataFrame(data_rows, columns=header)
        return df.to_html(index=False, escape=False)

    # Generate markdown report
    report_md = generate_markdown_summary_report(df)

    # Split into sections and convert tables to HTML
    html_sections = []
    for section in report_md.split('### '):
        if not section.strip():
            continue
        lines = section.strip().split('\n', 1)
        title = lines[0]
        content = lines[1] if len(lines) > 1 else ""
        # Convert markdown tables to HTML tables
        parts = []
        for part in content.split('\n\n'):
            if part.strip().startswith('|'):
                parts.append(md_table_to_html(part))
            else:
                parts.append(f"<p>{part.strip()}</p>")
        html_sections.append(f'<div class="section"><h2>{title}</h2>{"".join(parts)}</div>')

    # Compose final HTML
    html = f"""
    <html>
    <head>
    <title>JIRA Data Summary Report</title>
    {css}
    </head>
    <body>
    <h1>JIRA Data Summary Report</h1>
    <p>This report provides a concise overview and statistics for the JIRA data.</p>
    {''.join(html_sections)}
    </body>
    </html>
    """

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

# Usage after fetching your DataFrame:
save_html_summary_report(df, "jira_summary_report.html")