# load environment variables
from dotenv import load_dotenv
_ = load_dotenv(override=True)
import os

import streamlit as st
from graphs.build_graph import build_supervisor_graph

@st.cache_resource
def get_graph():
    print("Building the graph...")
    graph = build_supervisor_graph()
    print("Graph has been built.")
    return graph

graph = get_graph()

# Streamlit UI components
st.title("DevOpsAssist")
st.sidebar.image('images/Finastra-logo.jpg', use_container_width=True)

# Initialize session state to store chat history and query input
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# Display chat messages from history on app rerun
# Display chat history (with icons)
for chat_history in st.session_state.chat_history:
    with st.chat_message(chat_history["role"]):
        st.markdown(chat_history["content"])

# Get user input
query = st.chat_input("Type your query here")

if query:
    # Show user input immediately
    with st.chat_message("user"):
        st.markdown(query)

    # Generate response (can still show spinner)
    thread = {"configurable": {"thread_id": "1"}}

    results = []
    # Create a temporary placeholder for interim updates
    placeholder = st.empty()


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
            }, thread):

            # Optionally print something useful during the stream
            current_step = output.keys()
            placeholder.markdown(f"Running step: `{list(current_step)[0]}`")  # Or any useful info

            results.append(output)

    # Clear the placeholder after processing
    placeholder.empty()

    response = results[-1]['handle_response']['final_response']

    st.markdown("\n")
    st.markdown("\n")

    col3, col4 = st.columns([5, 1])
    with col3:
        st.markdown(
            f"<div style='text-align: left; font-style: italic;'>{response}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("\n")
    st.markdown("\n")

    with st.expander("Show Full Model Process", expanded=False):
        st.write("\n")
        st.write("\n")
        st.write(results[-1]['handle_response']['memory_chain'])

    if results[-1]['handle_response']['report_generation_response'] == "Report Generated":
        with open("reports/combined_report.html", "r") as file:
            report_content = file.read()
            components.html(
                report_content,
                height=800,
                scrolling=True,
            )

        # Add a download button for the report
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name="report.html",
            mime="text/html"
        )

    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })
    # Save assistant response
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })

    # Clear the input field
    st.session_state.query_input = ""
    #st.experimental_rerun()