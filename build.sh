#!/bin/bash
# Build script per Ren'Py Translator - crea un archivio zip da distribuire
# Uso: ./build.sh [versione]  es: ./build.sh 2.0.1

VERSION=${1:-"2.0.0"}
DIST_DIR="dist"
BUILD_NAME="RenPy-Translator-v${VERSION}"
BUILD_DIR="${DIST_DIR}/${BUILD_NAME}"

echo "[Translator Build] Version: ${VERSION}"

# Pulisci build precedente
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Copia file principali
cp translator_tool.py tr_extractor.py tr_parser.py tr_translator.py tr_writer.py "${BUILD_DIR}/"
cp start.sh start.bat pyproject.toml README.md README_it.md "${BUILD_DIR}/"
cp logo_48.png logo_256.png logo_512.png splash.png translator-gui.png "${BUILD_DIR}/"

# Copia UnRen Tools
cp -r "UnRen Tools" "${BUILD_DIR}/"

# Rendi start.sh eseguibile
chmod +x "${BUILD_DIR}/start.sh"

# Crea zip
cd "${DIST_DIR}"
zip -r "${BUILD_NAME}.zip" "${BUILD_NAME}"
cd ..

echo "[Translator Build] Done: ${DIST_DIR}/${BUILD_NAME}.zip"
