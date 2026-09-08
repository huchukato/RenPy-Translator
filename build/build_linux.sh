#!/usr/bin/env bash
# Crea un archivio .tar.gz autocontenuto per Linux con venv embeddato
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="RenPy-Translator"

VERSION=$(grep -E '^version\s*=\s*"' "$SCRIPT_DIR/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
VERSION="${VERSION:-2.2.0}"
RELEASE_NAME="${APP_NAME}-v${VERSION}-linux"
OUT_DIR="$SCRIPT_DIR/dist/${RELEASE_NAME}"

echo "[RenPy-Translator] Building ${RELEASE_NAME}..."

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Crea un venv Linux-compatibile
echo "[RenPy-Translator] Creating venv..."
python3 -m venv --copies "$OUT_DIR/.venv"
"$OUT_DIR/.venv/bin/pip" install --upgrade pip -q
"$OUT_DIR/.venv/bin/pip" install -q -r <(grep -E '^\s+"' "$SCRIPT_DIR/pyproject.toml" | sed 's/[",]//g' | awk '{print $1}')

# Copia file progetto
echo "[RenPy-Translator] Copying project files..."
cp \
    "$SCRIPT_DIR/pyproject.toml" \
    "$SCRIPT_DIR/translator_tool.py" \
    "$SCRIPT_DIR/ctk_components.py" \
    "$SCRIPT_DIR/tr_extractor.py" \
    "$SCRIPT_DIR/tr_parser.py" \
    "$SCRIPT_DIR/tr_translator.py" \
    "$SCRIPT_DIR/tr_writer.py" \
    "$OUT_DIR/"

cp -R "$SCRIPT_DIR/img" "$OUT_DIR/img"
cp -R "$SCRIPT_DIR/UnRen Tools" "$OUT_DIR/UnRen Tools"

# Copia settings di default se presente
[ -f "$SCRIPT_DIR/translator_settings.json" ] && cp "$SCRIPT_DIR/translator_settings.json" "$OUT_DIR/"

# Launcher script
cat > "$OUT_DIR/start.sh" <<'LAUNCHER'
#!/bin/bash
# RenPy-Translator - Linux Launcher (autocontenuto)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "[Translator] ERROR: Embedded Python not found."
    echo "Run this from the extracted archive directory."
    read -p "Press Enter to exit..."
    exit 1
fi

cd "$SCRIPT_DIR"
exec "$PYTHON" translator_tool.py
LAUNCHER
chmod +x "$OUT_DIR/start.sh"

# Crea archivio .tar.gz
TAR_FILE="$SCRIPT_DIR/dist/${RELEASE_NAME}.tar.gz"
rm -f "$TAR_FILE"
(cd "$SCRIPT_DIR/dist" && tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}")

echo "[RenPy-Translator] Done: $TAR_FILE"
