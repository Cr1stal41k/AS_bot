sudo apt-get install python3.10
curl -sSL https://install.python-poetry.org | python3.10
export PATH="/home/user/.local/bin:$PATH"
poetry env use python3.10
sudo apt-get install python3.10-dev
poetry install --no-dev
poetry run python -m src.main &
disown %1
