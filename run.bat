@echo off
title HomeHub Launcher
cd /d "%~dp0"

:loop
cls
echo ===================================================
echo               HomeHub Launcher v1.0
echo ===================================================
echo.

if exist venv\Scripts\activate.bat (
call venv\Scripts\activate
) else (
echo [WARNING] Virtual environment not found. Using system Python.
)

echo [INFO] Starting HomeHub Server...
python -m backend.main

if exist .update_ready (
echo.
echo [UPDATE] New version detected. Installing...
timeout /t 2 >nul

xcopy update_stage\* . /E /Y /H

rmdir /s /q update_stage
del .update_ready

echo [UPDATE] Successfully updated!
echo [INFO] Restarting server...
timeout /t 3 >nul
goto loop


)

echo.
echo [INFO] Server stopped manually.
pause