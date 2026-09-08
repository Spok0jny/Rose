@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title Rose - Symulator Znajomego (Test Party Mode)
cd /d "%~dp0"
python test_friend.py
echo.
pause
