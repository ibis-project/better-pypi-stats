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
    @pip install --upgrade -r requirements.txt

# dashboard
app:
    @quarto preview dashboard.qmd

# format
format:
    @ruff format .
