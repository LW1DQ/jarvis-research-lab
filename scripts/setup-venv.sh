#!/bin/bash
# setup-venv.sh - Create and configure Python virtual environment
# 2026-09-22

set -euo pipefail

RESEARCH_DIR="$HOME/research-jarvis"
VENV_DIR="$RESEARCH_DIR/.venv-science"

echo "🔧 Setting up Python virtual environment..."

# Check uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

# Install Python 3.12 if needed
uv python install 3.12

# Create venv
echo "Creating virtual environment at $VENV_DIR..."
uv venv --python 3.12 "$VENV_DIR"

# Activate and install dependencies
source "$VENV_DIR/bin/activate"
echo "Installing dependencies from config/requirements.txt..."
uv pip install -r "$RESEARCH_DIR/config/requirements.txt"

echo "✅ Virtual environment ready!"
echo "Activate with: source $VENV_DIR/bin/activate"