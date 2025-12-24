#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

if [ -z "$OPENAPI_URL" ]; then
    echo "Error: OPENAPI_URL environment variable is required"
    echo "Usage: OPENAPI_URL=http://localhost:8000/openapi.json ./run.sh"
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR"

.venv/bin/python -m src.main
