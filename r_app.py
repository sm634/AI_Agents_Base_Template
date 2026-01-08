# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

import streamlit as st
import streamlit.components.v1 as components
from graphs.build_graph import build_supervisor_graph
from tools.r_generate_report import generate_reports_tools
import psycopg2
from streamlit_option_menu import option_menu
import smtplib
from email.message import EmailMessage
from streamlit_free_text_select import st_free_text_select
import time
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import requests
import os

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Hide Streamlit's "Running..." spinner and status messages
# st.markdown("""
#     <style>
#     /* Hide the status widget and spinner overlay */
#     .stStatusWidget, .stStatusWidget > div {display: none !important;}
#     .st-emotion-cache-1v0mbdj {display: none !important;}
#     /* Hide the main running spinner and its text */
#     .stSpinner, .stSpinner > div, .stSpinner > div > div {display: none !important;}
#     /* Hide the "Running..." text that appears in the center */
#     .stAlert, .stNotification, .stMarkdown p {color: transparent !important;}
#     /* Hide the top-right running bar */
#     header [data-testid="stStatusWidget"] {display: none !important;}
#     </style>
# """, unsafe_allow_html=True)

def send_report_via_gmail(
    to_email,
    subject="Your DevOpsAssist Report",
    body="Please find the attached report.",
    report_path="reports/combined_report.html",
    from_email="sivajimanju11@gmail.com",
    from_password="yqny bukq oeit rsgd",
    smtp_server="smtp.gmail.com",
    smtp_port=587
):
    with open(report_path, "rb") as f:
        report_data = f.read()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    msg.add_attachment(report_data, maintype="text", subtype="html", filename="report.html")

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)

@st.cache_resource
def get_graph():
    print("Building the graph...")
    graph = build_supervisor_graph()
    print("Graph has been built.")
    return graph

graph = get_graph()

st.title("DevOpsAssist")
st.sidebar.image('images/Finastra-logo.jpg', use_container_width=True)
st.sidebar.image('images/devops.jpg', use_container_width=True)

# --- Sidebar: Report generation query and parameters ---
st.sidebar.markdown("## Generate Jira Inflows and Outflows Report")

column_options = [
    "🔴 Issue Type", "🟢 Status", "🔵 Assignee",
    "🟡 Summary", "🟣 Resolution", "🔵 Key", "🔴 Priority"
]
column_map = {col: col.split(" ", 1)[1] for col in column_options}

agg_functions = ["COUNT"]
chart_types = ["📊 bar", "🥧 pie", "📈 line"]
chart_type_map = {ct: ct.split()[1] for ct in chart_types}

selected_columns = st.sidebar.multiselect("Select columns", column_options, default=["🔴 Issue Type"])
selected_agg = st.sidebar.selectbox("Aggregate Function", agg_functions)
selected_chart = st.sidebar.selectbox("Chart Type", chart_types)
aggregate_by_options = ["Week", "Month", "3 Months"]
selected_aggregate_by = st.sidebar.selectbox("Aggregate by", aggregate_by_options)
generate_report_clicked = st.sidebar.button("Generate Report")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False

for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

suggestions = [
    "what is the release date of activemq 6.1.4?", "which version of jboss supports openjdk 11?", "Is azure sql tested/T for any OS platform?", "What is DevOps?",
    "how many tickets are open from last 1 year?", "How to deploy on Kubernetes?",
    "What is Jenkins?"
]

# --- Suggested Query Input Section ---
with st.form("query_form_suggested"):
    query = st_free_text_select(
        label="Type your query",
        options=suggestions,
        index=None,
        placeholder="Select or type your query",
        delay=100,
        key="chat_input_unique"
    )
    submitted = st.form_submit_button("Submit")

if submitted and query and query.strip():
    st.session_state.last_input = query.strip()
    msg = st.session_state.last_input
    st.session_state.chat_history.append({"role": "user", "content": msg})

    results = []
    placeholder = st.empty()

    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Processing..."):
        for output in graph.stream({
            'user_input': query,
            'supervisor_decision': '',
            'tool_calls': '',
            'agent_tool_retries': 0,
            'agent_max_tool_retries': 3,
            'postgres_query': '',
            'postgres_agent_response': '',
            'vector_db_agent_response': '',
            'report_generation_requested': '',
            'report_generation_response': '',
            'final_response': '',
            'memory_chain': []
        }, {"configurable": {"thread_id": "1"}}):
            current_step = output.keys()
            placeholder.markdown(f"Running step: `{list(current_step)[0]}`")
            results.append(output)

    placeholder.empty()

    response = results[-1]['handle_response']['final_response']

    col3, _ = st.columns([5, 1])
    with col3:
        st.markdown(f"<div style='text-align: left; font-style: italic;'>{response}</div>", unsafe_allow_html=True)

    with st.expander("Show Full Model Process", expanded=False):
        st.write(results[-1]['handle_response']['memory_chain'])

    if results[-1]['handle_response']['report_generation_response'] == "Report Generated":
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
            components.html(report_content, height=800, scrolling=True)
            st.download_button(
                label="Download Report",
                data=report_content,
                file_name="report.html",
                mime="text/html"
            )

            # --- Email Report Section ---
            with st.form("email_report_form"):
                st.markdown("#### Email the generated report")
                to_email = st.text_input("Recipient Email")
                send_email = st.form_submit_button("Send Report")
                if send_email and to_email:
                    try:
                        send_report_via_gmail(
                            to_email=to_email,
                            from_email="sivajimanju11@gmail.com",
                            from_password="yqny bukq oeit rsgd",
                        )
                        st.session_state["email_status"] = f"Report sent to {to_email}!"
                        st.session_state["email_status_type"] = "success"
                    except Exception as e:
                        st.session_state["email_status"] = f"Failed to send email: {e}"
                        st.session_state["email_status_type"] = "error"

            if "email_status" in st.session_state:
                if st.session_state["email_status_type"] == "success":
                    st.success(st.session_state["email_status"])
                else:
                    st.error(st.session_state["email_status"])

    # Save assistant reply
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- Report Display (After Manual Report Generation) ---
if generate_report_clicked:
    time_group = {
        "Week": "DATE_TRUNC('week', \"Created\")",
        "Month": "DATE_TRUNC('month', \"Created\")",
        "3 Months": "DATE_TRUNC('quarter', \"Created\")"
    }.get(selected_aggregate_by, "\"Created\"")

    group_by_list = []
    select_list = []

    for col in selected_columns:
        db_col = f'"{column_map[col]}"'
        group_by_list.append(db_col)
        select_list.append(db_col)

    group_by_list.append(time_group)
    select_list.append(f"{time_group} as period")

    agg_col = column_map[selected_columns[0]] if selected_columns else "Created"
    agg_expr = "COUNT(*)" if selected_agg == "COUNT" else f"{selected_agg}(\"{agg_col}\")"
    group_by = ", ".join(group_by_list)
    select_clause = ", ".join(select_list)
    sql_query = f"SELECT {select_clause}, {agg_expr} as agg_value FROM jira_data GROUP BY {group_by}"

    tool_input = {
        "query": sql_query,
        "chart_type": chart_type_map.get(selected_chart, "bar")
    }
    generate_reports_tools(tool_input)

    with open("reports/combined_report.html", "r") as file:
        report_content = file.read()
    st.session_state["report_ready"] = True
    st.session_state["report_content"] = report_content
    st.success("Report triggered with your selected parameters.")

if st.session_state.get("report_ready", False):
    report_content = st.session_state.get("report_content", "")
    if report_content:
        components.html(report_content, height=800, scrolling=True)
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name="report.html",
            mime="text/html"
        )

        # --- Email Report Section ---
        with st.form("email_report_form"):
            st.markdown("#### Email the generated report")
            to_email = st.text_input("Recipient Email")
            send_email = st.form_submit_button("Send Report")
            if send_email and to_email:
                try:
                    send_report_via_gmail(
                        to_email=to_email,
                        from_email="sivajimanju11@gmail.com",
                        from_password="yqny bukq oeit rsgd",
                    )
                    st.session_state["email_status"] = f"Report sent to {to_email}!"
                    st.session_state["email_status_type"] = "success"
                except Exception as e:
                    st.session_state["email_status"] = f"Failed to send email: {e}"
                    st.session_state["email_status_type"] = "error"

        if "email_status" in st.session_state:
            if st.session_state["email_status_type"] == "success":
                st.success(st.session_state["email_status"])
            else:
                st.error(st.session_state["email_status"])

# Place the Databox and ADO dashboard links before the feedback widget
st.sidebar.markdown(
    """
    <a href="https://app.databox.com/datawall/90c20598c98c269f52e641425d78e877215af70687a2d6f" target="_blank">
        📊 GitHub Dashboard
    </a>
    <br>
    <a href="https://dev.azure.com/CorporateBanking/FCC/_dashboards/dashboard/2626ece2-1dc3-42a2-859a-27bc2b639d9f" target="_blank">
        📈 ADO Dashboard
    </a>
    """,
    unsafe_allow_html=True
)

# --- Feedback Section (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Feedback")

with st.sidebar.form("feedback_form"):
    feedback_text = st.text_area("Your feedback", height=100)
    submit_feedback = st.form_submit_button("Submit Feedback")
    show_sentiment = st.form_submit_button("Show Sentiment Analysis")
    sentiment_label = ""
    sentiment_percent = None

    if (submit_feedback or show_sentiment) and feedback_text.strip():
        # Sentiment analysis for current feedback
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(feedback_text)
        compound = sentiment["compound"]
        sentiment_percent = int((compound + 1) * 50)  # Convert -1..1 to 0..100%
        sentiment_label = (
            "Positive 😊" if compound > 0.2 else
            "Negative 😞" if compound < -0.2 else
            "Neutral 😐"
        )

    if submit_feedback and feedback_text.strip():
        try:
            conn = psycopg2.connect(
                dbname="ibmclouddb",
                user="ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4",
                password="qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A",
                host="50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud",
                port="31244"
            )
            cur = conn.cursor()
            username = "anonymous"
            cur.execute(
                "INSERT INTO user_feedback (username, feedback, sentiment) VALUES (%s, %s, %s);",
                (username, feedback_text, sentiment_label)
            )
            conn.commit()
            cur.close()
            conn.close()
            st.sidebar.success(f"Thank you for your feedback!")
        except Exception as e:
            st.sidebar.error(f"Failed to submit feedback: {e}")

    if show_sentiment:
        try:
            conn = psycopg2.connect(
                dbname="ibmclouddb",
                user="ibm_cloud_9a3059c8_df57_4e99_ae38_a34e20de34d4",
                password="qko9r5ISR5ip4BFD3nr7n4yP5g0ykT9A",
                host="50e2a09d-d988-405b-b8de-7a885f365743.497129fd685f442ca4df759dd55ec01b.databases.appdomain.cloud",
                port="31244"
            )
            cur = conn.cursor()
            cur.execute("SELECT sentiment FROM user_feedback;")
            sentiments = [row[0] for row in cur.fetchall() if row[0] is not None]
            cur.close()
            conn.close()

            total = len(sentiments)
            pos = sum(1 for s in sentiments if "Positive" in s)
            neg = sum(1 for s in sentiments if "Negative" in s)
            neu = sum(1 for s in sentiments if "Neutral" in s)

            pos_percent = round((pos / total) * 100, 1) if total else 0
            neg_percent = round((neg / total) * 100, 1) if total else 0
            neu_percent = round((neu / total) * 100, 1) if total else 0

            st.sidebar.markdown(
                f"""
                <table style="width:100%;text-align:center;">
                    <tr>
                        <th>Label</th>
                        <th>Percentage</th>
                        <th>Count</th>
                    </tr>
                    <tr>
                        <td>Positive 😊</td>
                        <td>{pos_percent}%</td>
                        <td>{pos}</td>
                    </tr>
                    <tr>
                        <td>Neutral 😐</td>
                        <td>{neu_percent}%</td>
                        <td>{neu}</td>
                    </tr>
                    <tr>
                        <td>Negative 😞</td>
                        <td>{neg_percent}%</td>
                        <td>{neg}</td>
                    </tr>
                    <tr>
                        <td colspan="3"><b>Total Feedbacks: {total}</b></td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            st.sidebar.error(f"Failed to fetch overall sentiment analysis: {e}")

with st.spinner("Starting the application..."):
    graph = get_graph()


def get_azure_access_token():
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://management.azure.com/.default"
    }
    resp = requests.post(url, data=data)
    if resp.ok:
        return resp.json()["access_token"]
    else:
        raise Exception(f"Failed to get Azure access token: {resp.text}")
    
    
#access_token = os.environ.get("AZURE_ACCESS_TOKEN")
access_token = get_azure_access_token()
subscription_ids = os.environ.get("AZURE_SUBSCRIPTION_IDS", "")
subscription_ids = [sid.strip() for sid in subscription_ids.split(",") if sid.strip()]

#subscription_id = "7429c7e0-a55e-41e6-b5f5-a9c8bc499e8f"
#resource_group = "AZR-C33-QA-195-04"  # Replace with your resource group
vm_name = "l33q19504536004"                  # Your VM name
#access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuY29yZS53aW5kb3dzLm5ldC8iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9lMTdlMjQwMi0yYTQwLTQyY2UtYWQ3NS01ODQ4YjhkNGY2YjYvIiwiaWF0IjoxNzU0NzM2MDYwLCJuYmYiOjE3NTQ3MzYwNjAsImV4cCI6MTc1NDc0MDQ0NiwiX2NsYWltX25hbWVzIjp7Imdyb3VwcyI6InNyYzEifSwiX2NsYWltX3NvdXJjZXMiOnsic3JjMSI6eyJlbmRwb2ludCI6Imh0dHBzOi8vZ3JhcGgud2luZG93cy5uZXQvZTE3ZTI0MDItMmE0MC00MmNlLWFkNzUtNTg0OGI4ZDRmNmI2L3VzZXJzLzQyNGRiZGE5LTZkNmQtNDZmZS1iN2FhLWFmODZhNWU5NGU1Zi9nZXRNZW1iZXJPYmplY3RzIn19LCJhY3IiOiIxIiwiYWNycyI6WyJwMSIsImMyIl0sImFpbyI6IkFYUUFpLzhaQUFBQWNUcFVjZ0RvUmxWR2ZHV0h3cHduUTJSRTZKQWpSOTVsa3hVWFZidDRsRDlLdnRyUUZSNzVsRmNMVnFZQno1TlNnaUNHY3I2SkYrbzJxNlNMa2dHeWE2OFZVYkE3YUZmcHRCbTV1VzI1Yjd5aTdPV2laa241SHc1US9QdWY0OGZOQUk5OWEraTd2QWVBSFdJcTE5SUZRdz09IiwiYW1yIjpbInB3ZCIsIm1mYSJdLCJhcHBpZCI6IjA0YjA3Nzk1LThkZGItNDYxYS1iYmVlLTAyZjllMWJmN2I0NiIsImFwcGlkYWNyIjoiMCIsImRldmljZWlkIjoiYTkzNzY1Y2MtZjA5Ni00YTViLWFjMTMtMTIxNGUxN2UyNTYzIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMTM2LjIyNi4yNTAuMjA1IiwibmFtZSI6Ik5hbmRlZXNoIE1NIiwib2lkIjoiNDI0ZGJkYTktNmQ2ZC00NmZlLWI3YWEtYWY4NmE1ZTk0ZTVmIiwicHVpZCI6IjEwMDMyMDAzMDIwNDM3RTkiLCJyaCI6IjEuQVE0QUFpUi00VUFxemtLdGRWaEl1TlQydGtaSWYza0F1dGRQdWtQYXdmajJNQk1PQU0wT0FBLiIsInNjcCI6InVzZXJfaW1wZXJzb25hdGlvbiIsInNpZCI6IjAwN2IyYjU5LTExYzQtM2M2Ni05YjRhLWUwZDkxMjVmZjFiZSIsInN1YiI6IktTN2RSUjM2VFBVMU91YWJBV0JiNUhYX1V2ZjhXZ21HREU0TGo1VmpDQ2siLCJ0aWQiOiJlMTdlMjQwMi0yYTQwLTQyY2UtYWQ3NS01ODQ4YjhkNGY2YjYiLCJ1bmlxdWVfbmFtZSI6Im5hbmRlZXNoLm1tQGRoLmNvbSIsInVwbiI6Im5hbmRlZXNoLm1tQGRoLmNvbSIsInV0aSI6IjJSb3ZCaVBwTlVlUXVkRlVOVTQtQUEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfZnRkIjoiOG5ENmhqaFJLTktuemt4ZHk4TE9LNnhtWHc0VVBFMTMwNFFvbHM3b3J6QUJkWE51YjNKMGFDMWtjMjF6IiwieG1zX2lkcmVsIjoiMSAxNCIsInhtc190Y2R0IjoxMzgxNTAyOTgxfQ.fnzVlsRmhxSxSJr9YaX49urlASmD4Wn9bxLejJZmgfvvF1YsWofKb9jbHAQunlDfMLf4jMVtzTI7h5H-6LPdnvzVgA1YAjVhGDXDetvC4x16O7LZLsdbIBtySoe_2qgpcMhxy38Gaac9GKKGunzr-a_WaGv4QTKt1MwU937bIw-mhin7WaY8GYPR1vYZro3Ofpp1aO6POPMZQj-5hqMOyzzGydwsuQbOY9rIP6kOageU2r0zBOVE3hJ1v2_ZN-EXwIDwAHt_WeXvAApabDOBh_ecIyF8MDh3PifPpAlW_CQMucextymX3-dqk_9e-_wS1-fwFBN7mgIN8Y4H4znqcw"
# def get_azure_vm_status(subscription_id, resource_group, vm_name, access_token):
#     url = (
#         f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/"
#         f"{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}/instanceView"
#         "?api-version=2023-03-01"
#     )
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     response = requests.get(url, headers=headers)
#     if response.ok:
#         data = response.json()
#         for status in data.get("statuses", []):
#             if status["code"].startswith("PowerState/"):
#                 return status["displayStatus"]
#         return "Status not found"
#     else:
#         return f"Error: {response.text}"

# # --- Streamlit Widget for VM Status ---
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Azure VM Status Checker")

# with st.sidebar.form("vm_status_form"):
#     input_vm_name = st.text_input("Enter VM Name", value=vm_name)
#     check_vm = st.form_submit_button("Check VM Status")
#     vm_status_result = ""
#     if check_vm and input_vm_name.strip():
#         vm_status_result = get_azure_vm_status(
#             subscription_id=subscription_id,
#             resource_group=resource_group,
#             vm_name=input_vm_name.strip(),
#             access_token=access_token
#         )
#         st.sidebar.info(f"VM '{input_vm_name}': {vm_status_result}")
def find_resource_group_for_vm(subscription_id, vm_name, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    vms_url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Compute/virtualMachines?api-version=2023-03-01"
    all_vm_names = []
    while vms_url:
        vms_resp = requests.get(vms_url, headers=headers)
        if not vms_resp.ok:
            st.sidebar.error(f"Azure API error: {vms_resp.text}")
            return None
        data = vms_resp.json()
        for vm in data.get("value", []):
            all_vm_names.append(vm.get("name", ""))
            if vm.get("name", "").lower() == vm_name.lower():
                vm_id = vm.get("id", "")
                parts = vm_id.split("/")
                if "resourceGroups" in parts:
                    rg_index = parts.index("resourceGroups") + 1
                    return parts[rg_index]
        vms_url = data.get("nextLink")
    #st.sidebar.write("VMs found in subscription:", all_vm_names)  # Debug line
    return None

# st.sidebar.markdown("---")
# st.sidebar.markdown("### Find Resource Group by VM Name")

# with st.sidebar.form("find_rg_form"):
#     input_vm_name = st.text_input("Enter VM Name to find Resource Group")
#     find_rg = st.form_submit_button("Find Resource Group")
#     if find_rg and input_vm_name.strip():
#         found_rg = find_resource_group_for_vm(subscription_id, input_vm_name.strip(), access_token)
#         if found_rg:
#             st.sidebar.success(f"Resource Group: {found_rg}")
#         else:
#             st.sidebar.error("Resource Group not found for this VM.")

def get_azure_vm_details_and_status(subscription_id, resource_group, vm_name, access_token):
    base_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
    headers = {"Authorization": f"Bearer {access_token}"}

    # 1. Get VM configuration
    config_url = f"{base_url}?api-version=2023-03-01"
    config_resp = requests.get(config_url, headers=headers)
    config = config_resp.json() if config_resp.ok else {}

    # 2. Get VM status (instance view)
    status_url = f"{base_url}/instanceView?api-version=2023-03-01"
    status_resp = requests.get(status_url, headers=headers)
    status = status_resp.json() if status_resp.ok else {}

    # Parse status
    power_state = "Unknown"
    for s in status.get("statuses", []):
        if s["code"].startswith("PowerState/"):
            power_state = s["displayStatus"]

    # Parse config details
    vm_size = config.get("properties", {}).get("hardwareProfile", {}).get("vmSize", "N/A")
    os_type = config.get("properties", {}).get("storageProfile", {}).get("osDisk", {}).get("osType", "N/A")
    computer_name = config.get("properties", {}).get("osProfile", {}).get("computerName", "N/A")
    nic_ids = [nic["id"] for nic in config.get("properties", {}).get("networkProfile", {}).get("networkInterfaces", [])]
    disk_name = config.get("properties", {}).get("storageProfile", {}).get("osDisk", {}).get("name", "N/A")
    location = config.get("location", "N/A")
    
    # Get RAM and CPU info from Azure VM sizes API (if possible)
    ram_gb = "N/A"
    cpu_count = "N/A"
    if vm_size != "N/A":
        # Query Azure for VM size info
        sizes_url = (
            f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Compute/locations/"
            f"{location}/vmSizes?api-version=2023-03-01"
        )
        sizes_resp = requests.get(sizes_url, headers=headers)
        if sizes_resp.ok:
            sizes = sizes_resp.json().get("value", [])
            for size in sizes:
                if size.get("name") == vm_size:
                    ram_gb = f"{round(size.get('memoryInMB', 0) / 1024, 1)} GB"
                    cpu_count = size.get("numberOfCores", "N/A")
                    break

    return {
        "VM Name": computer_name,
        "Resource Group": resource_group,
        "VM Size": vm_size,
        "OS Type": os_type,
        "OS Disk": disk_name,
        "NIC IDs": nic_ids,
        "Location": location,
        "RAM": ram_gb,
        "CPU (Cores)": cpu_count,
        "Power State": power_state
    }

def find_vm_across_subscriptions(subscription_ids, vm_name, access_token):
    for sub_id in subscription_ids:
        rg = find_resource_group_for_vm(sub_id, vm_name, access_token)
        if rg:
            return sub_id, rg
    return None, None

# --- Streamlit Widget for VM Details and Status ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Azure VM Details & Status")

with st.sidebar.form("vm_details_form"):
    input_vm_name = st.text_input("Enter VM Name")
    check_vm = st.form_submit_button("Get VM Details & Status")
    if check_vm and input_vm_name.strip():
        found_sub, found_rg = find_vm_across_subscriptions(subscription_ids, input_vm_name.strip(), access_token)
        if found_sub and found_rg:
            details = get_azure_vm_details_and_status(
                subscription_id=found_sub,
                resource_group=found_rg,
                vm_name=input_vm_name.strip(),
                access_token=access_token
            )
            st.sidebar.markdown("**VM Configuration & Status**")
            table_html = """
            <style>
            .vm-table th {
                padding: 10px 16px;
                background: linear-gradient(90deg, #ede7f6 0%, #ce93d8 100%);
                color: #4a148c;
                font-weight: 700;
                border-bottom: 2px solid #ba68c8;
                text-align: left;
                font-size: 1.08em;
                letter-spacing: 0.5px;
            }
            .vm-table td {
                padding: 10px 16px;
                background: linear-gradient(90deg, #f3e5f5 0%, #ede7f6 100%);
                color: #111;
                border-bottom: 1px solid #d1c4e9;
                font-size: 1.06em;
                vertical-align: middle;
            }
            .vm-table tr:nth-child(even) td {
                background: linear-gradient(90deg, #ede7f6 0%, #f3e5f5 100%);
            }
            .vm-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 6px 24px rgba(103,58,183,0.10);
                margin-bottom: 1em;
                margin-top: 0.5em;
            }
            </style>
            <table class='vm-table'>
            """

            for k, v in details.items():
                # Color coding for Power State
                if k == "Power State":
                    color = (
                        "#21ba45" if "running" in str(v).lower()
                        else "#db2828" if "stopped" in str(v).lower()
                        else "#db2828" if "deallocated" in str(v).lower()
                        else "#fbbd08"
                    )
                    v = f"<span style='color:{color};font-weight:bold'>{v}</span>"
                # All other outputs: bold black
                elif isinstance(v, list):
                    v = "<br>".join(f"<span style='color:#111;font-weight:bold'>{x}</span>" for x in v)
                else:
                    v = f"<span style='color:#111;font-weight:bold'>{v}</span>"
                table_html += f"<tr><th>{k}</th><td>{v}</td></tr>"

            table_html += "</table>"
            st.sidebar.markdown(table_html, unsafe_allow_html=True)
        else:
            st.sidebar.error("VM not found in any provided subscription.")



