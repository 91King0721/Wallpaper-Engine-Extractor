@echo off
chcp 65001 >nul
title Build Standalone Windows .exe
cd /d "%~dp0.."

set NAME=WallpaperEngineExtractor
set DIST=dist_standalone

echo Building standalone Windows .exe...
echo.

if exist "%DIST%" rmdir /s /q "%DIST%"
if exist "%NAME%.spec" del "%NAME%.spec"

set PYINSTALLER_CONFIG_DIR=%TEMP%\pyinstaller_config
if not exist "%PYINSTALLER_CONFIG_DIR%" mkdir "%PYINSTALLER_CONFIG_DIR%"

pyinstaller --windowed --onefile --noconfirm ^
    --name "%NAME%" ^
    --add-data "extractor;extractor" ^
    --hidden-import "extractor.pkg" ^
    --hidden-import "extractor.tex" ^
    --hidden-import "extractor.utils" ^
    --hidden-import "tkinterdnd2" ^
    --collect-all "tkinterdnd2" ^
    --workpath "%TEMP%\pyinstaller_work" ^
    --distpath "%DIST%" ^
    gui.py

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

cd "%DIST%"
powershell -Command "Compress-Archive -Path '%NAME%.exe' -DestinationPath '%NAME%_Windows_standalone.zip' -Force"
cd ..

echo.
echo === Done ===
echo   %DIST%\%NAME%.exe
echo   %DIST%\%NAME%_Windows_standalone.zip
pause
