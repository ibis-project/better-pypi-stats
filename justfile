# justfile

# load environment variables
set dotenv-load

# aliases
alias fmt:=format
alias preview:=app

# list justfile recipes
default:
    just --list

# setup
setup:
    @pip install uv
    @uv pip install --upgrade -r requirements.txt

# dashboard
app:
    @streamlit run dashboard.py

# format
format:
    @ruff format .

# eda
eda:
    @ipython -i eda.py
