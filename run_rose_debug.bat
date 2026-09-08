@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Rose (Debug Console - Live Logs)
cd /d "c:\Users\rbast\source\repos\Rose"
echo ================================================================
echo   ROSE - DEBUG MODE (LIVE CONSOLE LOGS)
echo ================================================================
echo   Branch: feat/party-mode-lan (LAN Direct Connection)
echo   Console output is enabled. All [PARTY], [LCU], and error logs
echo   will stream directly in this window.
echo.
echo   Press Ctrl+C or close this window to stop Rose.
echo ================================================================
echo.
python main.py --verbose
echo.
echo ================================================================
echo   Rose has exited.
echo ================================================================
pause
