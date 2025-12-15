#!/bin/bash
# Start script for Qwen-Agentes

set -e

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the CLI
python -m src.main "$@"
