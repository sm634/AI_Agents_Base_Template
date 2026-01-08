ENV_NAME=base_agent_env
YAML_FILE=environment.yml

.PHONY: all
all: setup run

# Create or update the Conda environment
.PHONY: setup
setup:
	@echo "Creating/updating Conda environment from $(YAML_FILE)..."
	@chmod +x setup.sh
	@if conda info --envs | grep -q $(ENV_NAME); then \
		echo "Environment '$(ENV_NAME)' already exists. Updating..."; \
		conda env update -n $(ENV_NAME) -f $(YAML_FILE) --prune; \
	else \
		echo "Environment '$(ENV_NAME)' does not exist. Creating..."; \
		conda env create -f $(YAML_FILE); \
	fi

# Run the setup.sh script with an optional Python script
.PHONY: run
run:
	@echo "Activating env..."
	@bash ./setup.sh $(ENV_NAME) main.py

# Delete the environment
.PHONY: clean
clean:
	conda remove -y -n $(ENV_NAME) --all
