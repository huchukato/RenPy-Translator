#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "$(uname -s)" != "Darwin" ]; then
    echo "[RenPy-Translator] ERROR: build_all.sh must be run on macOS."
    exit 1
fi

for command in zip hdiutil; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "[RenPy-Translator] ERROR: required command not found: $command"
        exit 1
    fi
done

if [ ! -x "$PROJECT_DIR/.venv/bin/python" ]; then
    echo "[RenPy-Translator] ERROR: project virtual environment not found at .venv."
    exit 1
fi

echo "[RenPy-Translator] Building all releases available from macOS..."
"$SCRIPT_DIR/build.sh"
"$SCRIPT_DIR/build_win.sh"
"$SCRIPT_DIR/build_mac_app.sh"

echo
printf '%s\n' \
    "[RenPy-Translator] All macOS-compatible builds completed." \
    "[RenPy-Translator] Linux was skipped because its embedded environment must be built on Linux." \
    "[RenPy-Translator] Artifacts are available in: $PROJECT_DIR/dist"
