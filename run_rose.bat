@echo off
setlocal
cd /d "%~dp0"

:: Check for Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [Rose] Requesting Administrator privileges to stream live terminal logs...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k cd /d \"\"%~dp0\"\" && title Rose (Competitive Mode - Terminal Logs) && python main.py --verbose' -Verb RunAs"
    exit /b
)

title Rose (Competitive Mode - Terminal Logs)
echo ================================================================================
echo Starting Rose with Competitive Mode and live terminal logs...
echo ================================================================================
python main.py --verbose
pause
