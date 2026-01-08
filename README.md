# DevOpsAssist Pilot Repo 
An AI Agent used to help troubleshoot, debug and find information quickly, as well as record/create records. 

## Environment Set-up

### Using Conda

1. Navigate to the parent directory of the repo.

```
cd ...\DevOpsAssist
```

2. Run the following conda command:

```
conda env create -f environment.yml
```

3. Activate the environment:

```
conda activate devops_agent_env
```

### Using Python Venv

1. Navigate to the parent directory of the repo.

```
cd ...\DevOpsAssist
```
2. Run the following command on your terminal to create a virtual environment:

```
python3.12 -m venv devops_agent_env
```
3. Activate the Virtual Environment
  For macOS/Linux:
  ```
  source devops_agent_env/bin/activate
  ```
  For Windows:
  ```
  devops_agent_env\Scripts\activate
  ```

4. Install Dependencies from requirements.txt file
```
pip install --upgrade pip  # (optional, but recommended)
pip install -r requirements.txt
```
