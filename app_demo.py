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
