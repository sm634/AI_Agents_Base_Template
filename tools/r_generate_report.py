#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

class ReportGenerator(ABC):
    @abstractmethod
    def generate_report(self, df):
        pass

class HTMLReportGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/report.html'):
        html_table = df.to_html()
        with open(output_file, 'w') as f:
            f.write(html_table)
class MatplotlibChartGenerator:
    def __init__(self, chart_type="bar"):
        self.chart_type = chart_type.lower()

    def generate_report(self, df, output_file='reports/severity_chart.png'):
        print(f"Generating chart of type: {self.chart_type}")
        if df.empty:
            print("DataFrame is empty. Cannot generate chart.")
            return

        columns = df.columns.tolist()
        if "agg_value" in columns:
            group_cols = columns[:-1]
            agg_col = "agg_value"
        else:
            group_cols = [columns[0]]
            agg_col = None

        # Limit to top 30 categories for readability
        if agg_col and len(df) > 30:
            df = df.sort_values(by=agg_col, ascending=False).head(30)

        plt.figure(figsize=(20, 10), constrained_layout=True)

        if self.chart_type == "bar":
            if agg_col and len(group_cols) == 1:
                ax = sns.barplot(x=group_cols[0], y=agg_col, data=df)
                plt.title(f'Bar Chart of {agg_col} by {group_cols[0]}')
                plt.xlabel(group_cols[0])
                plt.ylabel(agg_col)
                plt.xticks(rotation=60, ha='right', fontsize=8)
                self._annotate_bars(ax)
            elif agg_col and len(group_cols) > 1:
                ax = sns.barplot(x=group_cols[0], y=agg_col, hue=group_cols[1], data=df)
                plt.title(f'Bar Chart of {agg_col} by {group_cols[0]} and {group_cols[1]}')
                plt.xlabel(group_cols[0])
                plt.ylabel(agg_col)
                plt.xticks(rotation=60, ha='right', fontsize=8)
                self._annotate_bars(ax)
            else:
                ax = sns.countplot(x=group_cols[0], data=df)
                plt.title(f'Bar Chart of {group_cols[0]}')
                plt.xlabel(group_cols[0])
                plt.ylabel('Count')
                plt.xticks(rotation=60, ha='right', fontsize=8)
                self._annotate_bars(ax)

        elif self.chart_type == "pie":
            if agg_col and len(group_cols) == 1:
                counts = df.set_index(group_cols[0])[agg_col]
                plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
                plt.title(f'Pie Chart of {agg_col} by {group_cols[0]}')
            else:
                counts = df[group_cols[0]].value_counts()
                plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
                plt.title(f'Pie Chart of {group_cols[0]}')

        elif self.chart_type == "line":
            if agg_col and len(group_cols) == 1:
                plt.plot(df[group_cols[0]], df[agg_col], marker='o')
                plt.title(f'Line Chart of {agg_col} by {group_cols[0]}')
                plt.xlabel(group_cols[0])
                plt.ylabel(agg_col)
            else:
                counts = df[group_cols[0]].value_counts().sort_index()
                plt.plot(counts.index, counts.values, marker='o')
                plt.title(f'Line Chart of {group_cols[0]}')
                plt.xlabel(group_cols[0])
                plt.ylabel('Count')
        else:
            print(f"Unknown chart type: {self.chart_type}")
            return

        plt.xticks(rotation=30, ha='right')
        plt.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.20)  
        plt.savefig(output_file)
        plt.close()

    def _annotate_bars(self, ax):
        for p in ax.patches:
            ax.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 10), textcoords='offset points')
# class MatplotlibChartGenerator(ReportGenerator):
#     def __init__(self, chart_type="bar"):
#         self.chart_type = chart_type.lower()

#     def generate_report(self, df, output_file='reports/severity_chart.png'):
#         print(f"Generating chart of type: {self.chart_type}")
#         if df.empty:
#             print("DataFrame is empty. Cannot generate chart.")
#             return

#         columns = df.columns.tolist()
#         if "agg_value" in columns:
#             group_cols = columns[:-1]
#             agg_col = "agg_value"
#         else:
#             group_cols = [columns[0]]
#             agg_col = None

#         # Limit to top 30 categories for readability
#         if agg_col and len(df) > 30:
#             df = df.sort_values(by=agg_col, ascending=False).head(30)

#         plt.figure(figsize=(20, 10), constrained_layout=True)

#         if self.chart_type == "bar":
#             if agg_col and len(group_cols) == 1:
#                 sns.barplot(x=group_cols[0], y=agg_col, data=df)
#                 plt.title(f'Bar Chart of {agg_col} by {group_cols[0]}')
#                 plt.xlabel(group_cols[0])
#                 plt.ylabel(agg_col)
#                 plt.xticks(rotation=60, ha='right', fontsize=8)
#             elif agg_col and len(group_cols) > 1:
#                 sns.barplot(x=group_cols[0], y=agg_col, hue=group_cols[1], data=df)
#                 plt.title(f'Bar Chart of {agg_col} by {group_cols[0]} and {group_cols[1]}')
#                 plt.xlabel(group_cols[0])
#                 plt.ylabel(agg_col)
#                 plt.xticks(rotation=60, ha='right', fontsize=8)
#             else:
#                 sns.countplot(x=group_cols[0], data=df)
#                 plt.title(f'Bar Chart of {group_cols[0]}')
#                 plt.xlabel(group_cols[0])
#                 plt.ylabel('Count')
#                 plt.xticks(rotation=60, ha='right', fontsize=8)

#         elif self.chart_type == "pie":
#             if agg_col and len(group_cols) == 1:
#                 counts = df.set_index(group_cols[0])[agg_col]
#                 plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
#                 plt.title(f'Pie Chart of {agg_col} by {group_cols[0]}')
#             else:
#                 counts = df[group_cols[0]].value_counts()
#                 plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
#                 plt.title(f'Pie Chart of {group_cols[0]}')

#         elif self.chart_type == "line":
#             if agg_col and len(group_cols) == 1:
#                 plt.plot(df[group_cols[0]], df[agg_col], marker='o')
#                 plt.title(f'Line Chart of {agg_col} by {group_cols[0]}')
#                 plt.xlabel(group_cols[0])
#                 plt.ylabel(agg_col)
#             else:
#                 counts = df[group_cols[0]].value_counts().sort_index()
#                 plt.plot(counts.index, counts.values, marker='o')
#                 plt.title(f'Line Chart of {group_cols[0]}')
#                 plt.xlabel(group_cols[0])
#                 plt.ylabel('Count')
#         else:
#             print(f"Unknown chart type: {self.chart_type}")
#             return

        # plt.xticks(rotation=30, ha='right')
        # plt.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.20)  # Add this line for more space
        # # Remove plt.tight_layout() if using constrained_layout
        # plt.savefig(output_file)
        # plt.close()


# class SeabornCountplotGenerator:
#     def generate_report(self, df, output_file='reports/combined_chart.png'):
#         if df.empty:
#             print("DataFrame is empty. Cannot generate chart.")
#             return
#         columns = df.columns.tolist()
#         if len(columns) < 2:
#             print("DataFrame must have at least two columns.")
#             return

#         x_column = columns[0]
#         hue_column = columns[1]
#         plt.figure(figsize=(10, 6))
#         if 'count' in columns:
#             sns.barplot(x=x_column, y='count', hue=hue_column, data=df)
#         else:
#             sns.countplot(x=x_column, hue=hue_column, data=df)
#         plt.title(f'Distribution of {hue_column} over {x_column}')
#         plt.xlabel(x_column)
#         plt.ylabel('Count')
#         plt.tight_layout()
#         plt.savefig(output_file)
#         plt.close()

# SummaryReport

class SummaryReportGenerator(ReportGenerator):
    def generate_report(self, df, output_file='reports/summary_report.html'):
        num_rows, num_cols = df.shape

        # Column Overview
        column_info_md = "| Column Name | Data Type |\n|---|---|\n"
        for col in df.columns:
            column_info_md += f"| {col} | {df[col].dtype} |\n"

        # Summary Statistics
        summary_stats = df.describe(include='all').T
        cols_to_keep = ['count', 'unique', 'top', 'freq']
        summary_stats_filtered = summary_stats[cols_to_keep].copy()
        if 'agg_value' in summary_stats_filtered.index:
            summary_stats_filtered = summary_stats_filtered.drop('agg_value')
        summary_stats_md = summary_stats_filtered.reset_index().to_markdown(index=False)

        # Categorical Distributions
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        categorical_dist_md = ""
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            categorical_dist_md += f"\n**{col}**\n\n"
            categorical_dist_md += value_counts.reset_index().rename(
                columns={'index': col, col: 'Count'}
            ).to_markdown(index=False)
            categorical_dist_md += "\n"

        # Timestamps
        time_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
        time_trend_md = ""
        if len(time_cols) > 0:
            for col in time_cols:
                min_time = df[col].min()
                max_time = df[col].max()
                time_trend_md += f"<div>- <b>{col}</b> ranges from <code>{min_time}</code> to <code>{max_time}</code></div>\n"
            time_col = time_cols[0]
            time_counts = df[time_col].dt.date.value_counts().sort_index()
            time_trend_md += "<br><b>Entries per day:</b><br>"
            time_trend_md += time_counts.reset_index().rename(
                columns={'index': 'Date', time_col: 'Count'}
            ).to_markdown(index=False)
        else:
            time_trend_md = "<i>No timestamp columns found.</i>"

        # Helper to convert Markdown tables to HTML
        import pandas as pd
        import re

        def md_table_to_html(md_table):
            lines = [line for line in md_table.strip().split('\n') if line.strip()]
            header_idx = None
            for i, line in enumerate(lines):
                if line.startswith('|') and line.endswith('|'):
                    header_idx = i
                    break
            if header_idx is None or header_idx + 1 >= len(lines):
                return f"<pre>{md_table}</pre>"
            header = [h.strip() for h in lines[header_idx].split('|')[1:-1]]
            sep_idx = header_idx + 1
            data_rows = []
            for line in lines[sep_idx+1:]:
                if not line.startswith('|'):
                    continue
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(row) < len(header):
                    row += [''] * (len(header) - len(row))
                elif len(row) > len(header):
                    row = row[:len(header)]
                data_rows.append(row)
            df_html = pd.DataFrame(data_rows, columns=header)
            return df_html.to_html(index=False, escape=False)

        # Convert all Markdown tables to HTML
        column_info_html = md_table_to_html(column_info_md)
        summary_stats_html = md_table_to_html(summary_stats_md)
        cat_html = ""
        for part in re.split(r"\*\*(.+?)\*\*", categorical_dist_md):
            if part.strip() and not part.strip().startswith('|'):
                cat_html += f"<h4>{part.strip()}</h4>"
            elif part.strip().startswith('|'):
                cat_html += md_table_to_html(part)
        time_trend_html = re.sub(r'((?:\|.*\|\n)+)', lambda m: md_table_to_html(m.group(1)), time_trend_md)

        # Business sections (to be placed after timestamps)
        business_sections = f"""
        <h2><u><i>Business Implications</i></u></h2>
        <p>The insights gained from this analysis have significant implications for the business. By leveraging DevOps Chat Assist, organizations can:</p>
        <ul>
            <li>Improve collaboration and communication among team members, leading to faster time to market and reduced costs.</li>
            <li>Enhance the reliability and efficiency of DevOps processes, resulting in improved customer satisfaction.</li>
        </ul><br/>

        <h2><u><i>Recommendations</i></u></h2>
        <p>Based on the findings of this analysis, we recommend that organizations:</p>
        <ul>
            <li>Implement DevOps Chat Assist to streamline DevOps processes and improve collaboration.</li>
            <li>Continuously monitor and analyze key metrics to identify areas for improvement and optimize DevOps processes.</li>
        </ul><br/>

        <h2><u><i>Conclusion</i></u></h2>
        <p>In conclusion, DevOps Chat Assist offers a range of benefits that can enhance the efficiency, collaboration, and reliability of DevOps teams. By leveraging this tool and following the recommendations outlined in this report, organizations can achieve significant improvements in their DevOps processes.</p>
        """

        # HTML template for summary report
        html_report = f"""
<div style="max-width:900px;margin:auto;background:#fff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08);padding:32px 40px;">
    <h1 style="color:#4B0082;text-align:center;">JIRA Data Summary Report</h1>
    <div style="font-size:1.1em;margin-bottom:1.5em;text-align:center;">
        <strong>Rows:</strong> {num_rows} &nbsp;&nbsp; <strong>Columns:</strong> {num_cols}
    </div>
    <h2><u><i>Introduction</i></u></h2>
    <p>DevOps Chat Assist represents a significant advancement in DevOps tooling, offering a range of features and benefits that can greatly enhance the efficiency, collaboration, and reliability of DevOps teams. By leveraging this tool, organizations can achieve faster time to market, reduced costs, and improved customer satisfaction.</p><br/>
    <h2><u><i>Key Insights</i></u></h2>
    <p>The analysis of the dataset reveals several key insights that can inform business decisions. These include:</p>
    <div class="section">
        <h2 style="color:#4B0082;">Column Overview</h2>
        {column_info_html}
    </div>
    <div class="section">
        <h2 style="color:#4B0082;">Summary Statistics</h2>
        {summary_stats_html}
    </div>
    <div class="section">
        <h2 style="color:#4B0082;">Categorical Distributions</h2>
        {cat_html}
    </div>
    <div class="section">
        <h2 style="color:#4B0082;">Timestamps</h2>
        {time_trend_html}
    </div>
    {business_sections}
</div>
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_report)

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

class CombinedReportGenerator(ReportGenerator):
    def __init__(self, report_generators, chart_type="bar"):
        self.report_generators = report_generators
        self.chart_type = chart_type

    def generate_report(self, df, output_file='reports/combined_report.html'):
        html_report = ''
        summary_report = ''

        for generator in self.report_generators:
            if isinstance(generator, HTMLReportGenerator):
                generator.generate_report(df, output_file='reports/temp.html')
                with open('reports/temp.html', 'r') as f:
                    html_report = f.read()
            elif isinstance(generator, MatplotlibChartGenerator):
                generator.generate_report(df, output_file='reports/severity_chart.png')
            elif isinstance(generator, SummaryReportGenerator):
                generator.generate_report(df, output_file='reports/summary_report.html')
                with open('reports/summary_report.html', "r", encoding="utf-8") as f:
                    summary_report = f.read()
            # elif isinstance(generator, SeabornCountplotGenerator):
            #     generator.generate_report(df, output_file='reports/combined_chart.png')
        # Choose the correct chart file
        if self.chart_type in ["pie", "line", "bar"]:
            chart_path = 'reports/severity_chart.png'
        else:
            chart_path = 'reports/combined_chart.png'
        chart_base64 = ""
        if os.path.exists(chart_path):
            with open(chart_path, "rb") as img_file:
                chart_base64 = base64.b64encode(img_file.read()).decode('utf-8')        
        html_report = ''
        summary_report = ''

        for generator in self.report_generators:
            if isinstance(generator, HTMLReportGenerator):
                generator.generate_report(df, output_file='reports/temp.html')
                with open('reports/temp.html', 'r') as f:
                    html_report = f.read()
            elif isinstance(generator, MatplotlibChartGenerator):
                generator.generate_report(df, output_file='reports/severity_chart.png')
            elif isinstance(generator, SummaryReportGenerator):
                generator.generate_report(df, output_file='reports/summary_report.html')
                with open('reports/summary_report.html', "r", encoding="utf-8") as f:
                    summary_report = f.read()
            # elif isinstance(generator, SeabornCountplotGenerator):
            #     generator.generate_report(df, output_file='reports/combined_chart.png')
        chart_base64 = ""
        chart_path = 'reports/severity_chart.png'
        if os.path.exists(chart_path):
            with open(chart_path, "rb") as img_file:
                chart_base64 = base64.b64encode(img_file.read()).decode('utf-8')        
        template = Template(r"""
<html>
<head>
    <title>Report</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #E6E6FA;
            background-image: url('C:\\Users\\u728383\\Desktop\\devops.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-size: 18px;
            margin: 0;
            padding: 0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        h1 {
            font-size: 48px;
            color: #4B0082;
            text-align: center;
            margin-top: 20px;
        }
        h2 {
            font-size: 36px;
            color: #4B0082;
            margin-bottom: 10px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            font-size: 18px;
        }
        th {
            background-color: #f0f0f0;
            color: #4B0082;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 5px;
            font-size: 18px;
            color: #4B0082;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            background: linear-gradient(to right, #E6E6FA, #D8BFD8);
            color: #4B0082;
            box-sizing: border-box;
            flex: 1;
            overflow-y: auto;
        }
        #summary-report {
            background: linear-gradient(to right, #E6E6FA, #D8BFD8);
            color: #4B0082;
            font-size: 24px;
            flex: 1;
            overflow-y: auto;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            margin-bottom: 20px;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: 1px solid #4B0082;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            color: #4B0082;
            font-size: 18px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #ccc;
        }

        /* Responsive styling */
        @media (max-width: 768px) {
            body {
                font-size: 16px;
            }
            h1 {
                font-size: 36px;
            }
            h2 {
                font-size: 28px;
            }
            th, td {
                font-size: 16px;
                padding: 10px;
            }
            .tab button {
                font-size: 16px;
                padding: 12px 14px;
            }
        }

        @media (max-width: 480px) {
            body {
                font-size: 14px;
            }
            h1 {
                font-size: 28px;
            }
            h2 {
                font-size: 24px;
            }
            th, td {
                font-size: 14px;
                padding: 8px;
            }
            .tab button {
                font-size: 14px;
                padding: 10px 12px;
            }
        }
    </style>
</head>
<body>
    <h1>Report</h1>
    <div class="tab">
        <button class="tablinks" onclick="openTab(event, 'html-report')">HTML Report</button>
        <button class="tablinks" onclick="openTab(event, 'chart')">Chart</button>
        <button class="tablinks" onclick="openTab(event, 'summary-report')">Summary Report</button>
    </div>
    <div id="html-report" class="tabcontent">
        <h2>HTML Report</h2>
        {{ html_report }}
    </div>
    <div id="chart" class="tabcontent">
        <h2>Chart</h2>
        <img src="data:image/png;base64,{{ chart_base64 }}" alt="Severity Chart" />
    </div>
    <div id="summary-report" class="tabcontent">
        <h2>Summary Report</h2>
        <pre>{{ summary_report }}</pre>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>
""")
        # Generate reports using the provided generators
        html_report = ''
        summary_report = ''

        for generator in self.report_generators:
            if isinstance(generator, HTMLReportGenerator):
                generator.generate_report(df, output_file='reports/temp.html')
                with open('reports/temp.html', 'r') as f:
                    html_report = f.read()
            elif isinstance(generator, MatplotlibChartGenerator):
                generator.generate_report(df, output_file='reports/severity_chart.png')
            elif isinstance(generator, SummaryReportGenerator):
                generator.generate_report(df, output_file='reports/summary_report.html')
                with open('reports/summary_report.html', "r", encoding="utf-8") as f:
                    summary_report = f.read()
            # elif isinstance(generator, SeabornCountplotGenerator):
            #     generator.generate_report(df, output_file='reports/combined_chart.png')
        html_content = template.render(html_report=html_report, summary_report=summary_report, chart_base64=chart_base64)

        with open(output_file, 'w') as f:
            f.write(html_content)

class ReportAgent:
    def __init__(self, data_fetcher, report_generators, combined_report_generator=None):
        self.data_fetcher = data_fetcher
        self.report_generators = report_generators
        self.combined_report_generator = combined_report_generator

    def generate_reports(self, query):
        df = self.data_fetcher.fetch_data(query)
        if df is not None:
            for generator in self.report_generators:
                generator.generate_report(df)
            
            if self.combined_report_generator:
                self.combined_report_generator.generate_report(df)
            
            return "Reports generated successfully."
        else:
            return "Failed to generate reports due to a database error."

class GenerateReportsInput(BaseModel):
    query: str = "SQL query to fetch data for report generation"
    chart_type: str = "bar"



@tool(args_schema=GenerateReportsInput)
def generate_reports_tools(query: str, chart_type: str = "bar"):
    
    """
    This function generates reports based on the provided input data.
    """


    connector = PostgresConnector()
    data_fetcher = DataFetcher(connector)

    html_generator = HTMLReportGenerator()
    matplotlib_generator = MatplotlibChartGenerator(chart_type=chart_type)
    summary_generator = SummaryReportGenerator()
    # seaborn_generator = SeabornCountplotGenerator()
    # Create a list of report generators    
    report_generators = [html_generator, matplotlib_generator, summary_generator]
    # Create a combined report generator
    combined_report_generator = CombinedReportGenerator(report_generators, chart_type=chart_type)
    report_agent = ReportAgent(data_fetcher, report_generators, combined_report_generator)
    report_agent.generate_reports(query)
    return "Report Generated"

class GenerateSQLQuery(BaseModel):
    user_input: str = Field(description="The user input to be translated to SQL query to run.")
    system_prompt: Any = Field(description="The prompt to be used to help the LLM generate the SQL query to run.")
    llm: Any = Field(description="The LLM to use for generating the SQL query.")

@tool(args_schema=GenerateSQLQuery)
def generate_query(user_input: str, system_prompt: str, llm: Any) -> Dict[str, Any]:
    """
    Generates the SQL query based on the user input.
    :param user_input: The user input.
    :param system_prompt: The system prompt to use for generating the SQL query.
    :param llm: The LLM to use for generating the SQL query.
    :return: A dictionary containing the SQL query.
    """
    user_input = HumanMessage(content=user_input)
    messages = [system_prompt, user_input]
    response = llm.invoke(messages)
    query = response.content
    return {"query": query}

class QueryInput(BaseModel):
    query: str = Field(description="The SQL query for Postgres to run.")
    params: Any = Field(description="The parameters for the query to configure it/optimize it.")

@tool(args_schema=QueryInput)
def run_query(query: str, params=None):
    """
    A tool to generate SQL query based on user input and run that query on the Postgres database.
    :param query: The SQL query to run.
    :param params: The parameters for the query to configure it/optimize it.
    :return: The output of the SQL query.
    """
    try:
        pg_connector = PostgresConnector()
        response = pg_connector.run_query(query=query, params=params)
    except Exception as e:
        response = {"status": "error", "error": str(e)}
    return response

# Integrate the tools into the ReportAgent
class ReportAgentWithTools(ReportAgent):
    def __init__(self, data_fetcher, report_generators, combined_report_generator=None):
        super().__init__(data_fetcher, report_generators, combined_report_generator)

    def generate_reports_with_tools(self, table_name, columns, conditions=""):
        query = generate_sql_query(table_name, columns, conditions)
        df = run_query(query)
        if df is not None:
            for generator in self.report_generators:
                generator.generate_report(df)
            
            if self.combined_report_generator:
                self.combined_report_generator.generate_report(df)
            
            return "Reports generated successfully."
        else:
            return "Failed to generate reports due to a database error."

