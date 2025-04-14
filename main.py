from src.build_graph import build_graph


if __name__ == "__main__":
    
    graph = build_graph()

    with open("graph_output.png", "wb") as image_file:
        image_file.write(graph.get_graph().draw_png())
    
    print("Graph has been built and saved as graph_output.png")

    # for vectordb test
    user_input="What are some issues with noise on a ventilation system?"
    # for maximo test
    # user_input = "What is the status, description and priority of work order number 5012?"
    result = graph.invoke(
            {
                "user_input": user_input
            },
        )
    print(result)

    breakpoint()
