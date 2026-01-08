#!/bin/bash

ENV_NAME="base_agent_env"
SCRIPT=$1

# Load Conda into the shell session
source "$HOME/.bashrc"

# Activate the environment
echo "Activating conda environment: $ENV_NAME"
conda init
conda activate "$ENV_NAME"
