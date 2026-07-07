#!/bin/bash
set -e

source /invoice_ai/.venv/bin/activate

echo "User: $(whoami)"
echo "Home: $HOME"
echo "Working dir: $(pwd)"
echo "Python: $(which python3)"
echo "PATH: $PATH"
echo "Venv exists: $(ls /invoice_ai/.venv/bin/python 2>/dev/null && echo YES || echo NO)"

echo "Running Migration..."
uv run app/migrations/recreate_table.py

echo "Starting app..."
exec uv run app/main.py