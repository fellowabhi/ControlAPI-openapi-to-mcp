#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

export PYTHONPATH="$SCRIPT_DIR/src:$SCRIPT_DIR"

.venv/bin/python -m main
