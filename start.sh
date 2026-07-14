#!/bin/bash
# Ren'Py Translator - macOS/Linux Launcher

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v uv &>/dev/null; then
    echo "[Translator] uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv &>/dev/null; then
    echo "[Translator] ERROR: uv installation failed."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[Translator] Starting..."
cd "$SCRIPT_DIR"
PYTHON_BIN=$(command -v python3 || command -v python)
uv run --python "$PYTHON_BIN" translator_tool.py
