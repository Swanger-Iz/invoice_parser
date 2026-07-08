#!/bin/bash
set -e

echo "Current working dir: $(pwd)"

echo "User: $(whoami)"
echo "Home: $HOME"
echo "Working dir: $(pwd)"
echo "Python: $(which python3)"
echo "PATH: $PATH"
echo "Venv exists: $(ls /invoice_ai/.venv/bin/python 2>/dev/null && echo YES || echo NO)"

echo "Running Migration..."
uv run --no-sync app/migrations/recreate_table.py

echo "Starting app..."
exec uv run --no-sync app/main.py -m docker