#!/bin/bash
# Build script per Ren'Py Translator - crea un archivio zip da distribuire
# Versione letta automaticamente da pyproject.toml

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

VERSION=$(grep -E '^version\s*=\s*"' pyproject.toml | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
PROJECT_NAME="RenPy-Translator"
RELEASE_NAME="${PROJECT_NAME}-v${VERSION}"
OUT_DIR="dist/${RELEASE_NAME}"
ZIP_FILE="dist/${RELEASE_NAME}.zip"

echo "[Translator Build] Building release ${RELEASE_NAME}..."

# Pulisci build precedente
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Copia file principali
cp translator_tool.py tr_extractor.py tr_parser.py tr_translator.py tr_writer.py "$OUT_DIR/"
cp start.sh start.bat pyproject.toml README.md README_it.md "$OUT_DIR/"
cp -r img "$OUT_DIR/"

# Copia UnRen Tools
cp -r "UnRen Tools" "$OUT_DIR/"

# Rendi start.sh eseguibile
chmod +x "$OUT_DIR/start.sh"

# Crea zip
rm -f "$ZIP_FILE"
(cd dist && zip -r "${RELEASE_NAME}.zip" "${RELEASE_NAME}")

echo "[Translator Build] Done: $ZIP_FILE"
