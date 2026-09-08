@echo off
REM ============================================================
REM  RenPy-Translator - Build Windows .exe con PyInstaller
REM  Da eseguire nella bottle CrossOver (Python 3.13 + pip + pyinstaller)
REM
REM  Uso:
REM    cd /d Z:\Volumes\NVME\dev-ai\RenPy-Translator
REM    build\build_win_exe.bat
REM ============================================================
setlocal enableextensions

cd /d "%~dp0\.."
echo [RenPy-Translator] Working directory: %CD%

REM --- Verifica Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [RenPy-Translator] ERROR: python non trovato nel PATH.
    exit /b 1
)

python --version

REM --- Verifica PyInstaller ---
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [RenPy-Translator] PyInstaller non installato, lo installo...
    python -m pip install --upgrade pyinstaller
)

REM --- Verifica dipendenze progetto ---
python -c "import customtkinter, PIL, requests, httpx, deep_translator" 2>nul
if errorlevel 1 (
    echo [RenPy-Translator] Dipendenze mancanti, le installo...
    python -m pip install --upgrade customtkinter pillow deep-translator requests httpx
)

REM --- Pulizia build precedenti ---
echo [RenPy-Translator] Pulizia build precedenti...
if exist _pyi_build rmdir /s /q _pyi_build
if exist dist rmdir /s /q dist
if exist RenPy-Translator.spec del /q RenPy-Translator.spec

REM --- PyInstaller build ---
echo [RenPy-Translator] Avvio PyInstaller...
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --workpath _pyi_build ^
    --windowed ^
    --onedir ^
    --name RenPy-Translator ^
    --collect-all customtkinter ^
    --add-data "img;img" ^
    --add-data "UnRen Tools;UnRen Tools" ^
    translator_tool.py

if errorlevel 1 (
    echo [RenPy-Translator] ERROR: build PyInstaller fallita.
    exit /b 1
)

REM --- Verifica artefatto ---
if not exist "dist\RenPy-Translator\RenPy-Translator.exe" (
    echo [RenPy-Translator] ERROR: RenPy-Translator.exe non trovato.
    exit /b 1
)

echo [RenPy-Translator] Build completata: dist\RenPy-Translator\RenPy-Translator.exe

REM --- Crea zip finale ---
set "VERSION="
for /f "tokens=2 delims==" %%v in ('findstr /r "^version" pyproject.toml') do (
    set "VERSION=%%v"
)
if defined VERSION set "VERSION=%VERSION:"=%"

if not defined VERSION set "VERSION=0.0.0"

set "ZIP_NAME=RenPy-Translator-v%VERSION%-win-exe"
set "ZIP_PATH=dist\%ZIP_NAME%.zip"

echo [RenPy-Translator] Creazione pacchetto %ZIP_NAME%.zip...
if exist "dist\%ZIP_NAME%" rmdir /s /q "dist\%ZIP_NAME%"
xcopy /e /i /q "dist\RenPy-Translator" "dist\%ZIP_NAME%" >nul

powershell -NoProfile -Command "Compress-Archive -Path 'dist\%ZIP_NAME%' -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 (
    echo [RenPy-Translator] WARNING: powershell Compress-Archive non disponibile, salto lo zip.
    echo [RenPy-Translator] Cartella pronta: dist\%ZIP_NAME%
) else (
    echo [RenPy-Translator] Pacchetto creato: %ZIP_PATH%
)

endlocal
