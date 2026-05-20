@echo off
chcp 65001 >nul
title Wallpaper Engine Media Extractor
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required! Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
cd /d "%~dp0"
python src/gui.py
pause
