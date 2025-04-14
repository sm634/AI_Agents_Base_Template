import streamlit as st
from src.build_graph import build_graph

# initiate the graph_build
graph = build_graph()

# Streamlit UI components
st.title("BPD Agent")
st.sidebar.image('images/BPD logo.png', use_container_width=True)
st.subheader("Agent to Assist you with Maximo Work Orders")

import streamlit as st

# Initialize session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query = st.text_input("Type your query here")

col1, col2 = st.columns([1, 5])
# When query is submitted (Enter pressed)
if query:
    with col2:
        st.markdown(
            f"<div style='text-align: right; font-style: italic;'>{query}</div>",
            unsafe_allow_html=True,
        )
    # Generate response (can still show spinner)
    with st.spinner("Generating response..."):
        result = graph.invoke({
            "user_input": query
        })

    response = result['final_response']

    st.markdown("\n")

    col3, col4 = st.columns([5, 1])
    with col3:
        st.markdown(
            f"<div style='text-align: left; font-style: italic;'>{response}</div>",
            unsafe_allow_html=True,
        )

    with st.expander("Show Full Model Process", expanded=False):
        st.write("\n\n")
        st.write(result['memory_chain'])

    # Save query and response to session_state
    st.session_state.chat_history.append({
        "query": query,
        "response": response,
        "raw": result['memory_chain']
    })
