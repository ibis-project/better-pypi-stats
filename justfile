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
    @uv venv
    @. .venv/bin/activate
    @uv pip install --upgrade --resolution=highest -r dev-requirements.txt

# dashboard
app:
    @shiny run dashboard/app.py -b

# format
format:
    @ruff format .

# eda
eda:
    @ipython -i eda.py

# deploy
deploy:
    @rsconnect deploy shiny dashboard --name dkdc --title better-pypi-stats 

# open
open:
    @open https://dkdc.shinyapps.io/better-pypi-stats
