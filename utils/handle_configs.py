from config import Config
from typing import Dict
from langchain_ibm import ChatWatsonx
import os

def get_llm(config: Dict):
    """
    Handles the configuration parameters for instantiating the Watsonx Model.
    :param param_name: The name of the parameter to be handled.
    :return: The configuration parameters for the agent.
    """
    model_id = config['model_id']
    model_params = config['model_parameters']
    
    # instantiate the model with the parameters.
    llm = ChatWatsonx(
        model_id=model_id,
        url=os.environ["WATSONX_URL"],
        apikey=os.environ["WATSONX_APIKEY"],
        project_id=os.environ["WATSONX_PROJECT_ID"],
        params=model_params
    )

    return llm