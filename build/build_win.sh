#!/usr/bin/env bash
# Crea un archivio .zip autocontenuto per Windows
# NOTA: Deve essere eseguito su Windows (o con Python Windows in PATH per creare il venv).
#       In alternativa, eseguire su macOS/Linux per creare la struttura senza venv
#       e generare il venv al primo avvio su Windows.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="RenPy-Translator"

VERSION=$(grep -E '^version\s*=\s*"' "$SCRIPT_DIR/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
VERSION="${VERSION:-2.2.0}"
RELEASE_NAME="${APP_NAME}-v${VERSION}-win"
OUT_DIR="$SCRIPT_DIR/dist/${RELEASE_NAME}"

echo "[RenPy-Translator] Building ${RELEASE_NAME}..."

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

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

# Launcher .bat che crea il venv al primo avvio e poi esegue
cat > "$OUT_DIR/start.bat" <<'LAUNCHER'
@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    goto :run
)

echo [Translator] First run: creating virtual environment...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [Translator] ERROR: Python not found. Install Python 3.9+ from python.org
    pause
    exit /b 1
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo [Translator] ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo [Translator] Installing dependencies...
.venv\Scripts\pip install --upgrade pip -q
for /f "tokens=1 delims=," %%a in ('findstr /r "\"[a-z]" pyproject.toml') do (
    for /f "tokens=1 delims= " %%b in ("%%~a") do (
        .venv\Scripts\pip install -q %%b
    )
)

:run
echo [Translator] Starting...
.venv\Scripts\python translator_tool.py
pause
LAUNCHER

# Crea zip
ZIP_FILE="$SCRIPT_DIR/dist/${RELEASE_NAME}.zip"
rm -f "$ZIP_FILE"
(cd "$SCRIPT_DIR/dist" && zip -r "${RELEASE_NAME}.zip" "${RELEASE_NAME}")

echo "[RenPy-Translator] Done: $ZIP_FILE"
