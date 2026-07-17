#!/usr/bin/env bash
# Crea un bundle .app macOS autocontenuto per RenPy-Translator
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="RenPy-Translator"
BUNDLE_DIR="$SCRIPT_DIR/dist/${APP_NAME}.app"
PROJECT_DIR="$BUNDLE_DIR/Contents/Resources/project"
ICONSET_DIR="$SCRIPT_DIR/img/icon.iconset"
ICNS_SRC="$SCRIPT_DIR/img/logo.icns"

VERSION=$(grep -E '^version\s*=\s*"' "$SCRIPT_DIR/pyproject.toml" | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
VERSION="${VERSION:-2.1.0}"

echo "[RenPy-Translator] Building ${APP_NAME}.app v${VERSION}..."

rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/Contents/MacOS"
mkdir -p "$PROJECT_DIR"

# Copia dentro il bundle i file necessari a far girare la GUI
echo "[RenPy-Translator] Copying project into bundle..."
cp -R "$SCRIPT_DIR/.venv" "$PROJECT_DIR/.venv"
cp -R "$SCRIPT_DIR/img" "$PROJECT_DIR/img"

cp \
    "$SCRIPT_DIR/pyproject.toml" \
    "$SCRIPT_DIR/translator_tool.py" \
    "$SCRIPT_DIR/tr_extractor.py" \
    "$SCRIPT_DIR/tr_parser.py" \
    "$SCRIPT_DIR/tr_translator.py" \
    "$SCRIPT_DIR/tr_writer.py" \
    "$SCRIPT_DIR/translator_settings.json" \
    "$PROJECT_DIR/"

# Copia UnRen Tools
cp -R "$SCRIPT_DIR/UnRen Tools" "$PROJECT_DIR/UnRen Tools"

# Crea o copia l'icona .icns
ICNS_FILE="$BUNDLE_DIR/Contents/Resources/${APP_NAME}.icns"
if command -v iconutil &>/dev/null && [ -d "$ICONSET_DIR" ]; then
    if iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE" 2>/dev/null; then
        echo "[RenPy-Translator] Generated icns from icon.iconset."
    else
        cp "$ICNS_SRC" "$ICNS_FILE"
        echo "[RenPy-Translator] iconutil failed, using img/logo.icns."
    fi
else
    cp "$ICNS_SRC" "$ICNS_FILE"
    echo "[RenPy-Translator] iconutil not found, using img/logo.icns."
fi

# Info.plist
cat > "$BUNDLE_DIR/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.huchukato.renpy-translator</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Script di lancio autocontenuto
cat > "$BUNDLE_DIR/Contents/MacOS/${APP_NAME}" <<'LAUNCHER'
#!/usr/bin/env bash
# Launcher autocontenuto per RenPy-Translator.app

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$APP_DIR/../Resources/project"
cd "$PROJECT"

PYTHON="$PROJECT/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    osascript -e 'display dialog "Python virtualenv not found inside the app bundle." buttons {"OK"} default button 1' &
    exit 1
fi

PYTHON_BASE=$("$PYTHON" -c "import sys; print(sys.base_prefix)")
if [ -d "$PYTHON_BASE/lib/tcl8.6" ]; then
    export TCL_LIBRARY="$PYTHON_BASE/lib/tcl8.6"
fi
if [ -d "$PYTHON_BASE/lib/tk8.6" ]; then
    export TK_LIBRARY="$PYTHON_BASE/lib/tk8.6"
fi

export PYTHONPATH="$PROJECT"
exec "$PYTHON" "$PROJECT/translator_tool.py"
LAUNCHER

chmod +x "$BUNDLE_DIR/Contents/MacOS/${APP_NAME}"

echo "[RenPy-Translator] Bundle ready: $BUNDLE_DIR"
