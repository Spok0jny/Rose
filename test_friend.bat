@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Rose - Friend Simulator (Party Mode Test)
cd /d "%~dp0"
python test_friend.py
echo.
pause
