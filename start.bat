@echo off
setlocal

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [Translator] uv not found. Installing...
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
)

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [Translator] ERROR: uv installation failed.
    pause
    exit /b 1
)

echo [Translator] Starting...
cd /d "%~dp0"
uv run translator_tool.py
pause
