"""
Storing Config information for model, parameters, task and other Agent-level hyperparameters
"""

class Config:
    base_agent_params = {
        "model_parameters": {
            "decoding_method": "sample",
            "max_new_tokens": 2000,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "tools": []
    }
    supervisor_router_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 3,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "ibm/granite-3-8b-instruct"
    }
    supervisor_evaluator_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1000,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    }
    supervisor_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1000,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    }
    maximo_payload_generator_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 500,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
    }
    maximo_agent_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 500,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "mistralai/mistral-large"
    }
    vector_db_agent_params = {
        "model_parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 3000,
            "min_new_tokens": 1,
            "temperature": 0.0,
            "top_k": 50,
            "top_p": 1,
        },
        "model_id": "mistralai/mistral-large"
    }
