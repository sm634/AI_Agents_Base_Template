import streamlit as st
from src.build_graph import build_graph

# initiate the graph_build
graph = build_graph()

# Streamlit UI components
st.title("BPD Agent")
st.sidebar.image('images/BPD logo.png', use_container_width=True)
st.subheader("Agent to Assist you with Maximo Work Orders")

# with col1:
query = st.text_input("Type your query here")
if st.button("Ask") and query is not None:
    st.write(query)
    with st.spinner("Generating response..."):
        result = graph.invoke({
                "user_input": query
            },
        )
    
    st.write(result['memory_chain'][-1]['final_response'])

    expander_msg = f"Show Full Model Process"
    with st.expander(expander_msg):
        st.write(result)
