@echo off
setlocal enabledelayedexpansion

title MHDDoS Professional Tactical Web Interface
echo [*] Initializing MHDDoS Professional Launcher...

:: Change to script directory
cd /d "%~dp0"

:: 1. Virtual Environment Detection
if exist ".venv\Scripts\activate.bat" (
    echo [*] Detected Poetry virtual environment. Activating...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [*] Detected virtual environment. Activating...
    call venv\Scripts\activate.bat
) else (
    echo [!] Warning: 'venv' or '.venv' directory not found.
    echo [*] Attempting to run using system default Python...
)

:: 2. Launch Application
echo [*] Starting MHDDoS GUI Module...
:: Python handles Redis and Terminal Output piping now
python -m src.gui.web_runner %*

:: 3. Error Handling / Persistence
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Critical Error: Application exited with code %ERRORLEVEL%.
    echo [*] Please review the logs above for troubleshooting.
    pause
) else (
    echo [*] Application closed normally.
)

endlocal
