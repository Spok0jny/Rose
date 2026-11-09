@echo off
setlocal
cd /d "%~dp0"

:: Check for Administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [Rose] Requesting Administrator privileges to run Rose.exe with live logs...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/k cd /d \"\"%~dp0\"\" && title Rose.exe (Competitive Mode - Terminal Logs) && dist\Rose\Rose.exe --verbose' -Verb RunAs"
    exit /b
)

title Rose.exe (Competitive Mode - Terminal Logs)
echo ================================================================================
echo Starting compiled dist\Rose\Rose.exe with Competitive Mode and live logs...
echo ================================================================================
dist\Rose\Rose.exe --verbose
pause
