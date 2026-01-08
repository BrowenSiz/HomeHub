@echo off
title HomeHub Launcher
cd /d "%~dp0"

:loop
cls
echo [HomeHub] Starting...

if exist HomeHub.exe (
echo Launching application...
HomeHub.exe
) else (
echo [ERROR] HomeHub.exe not found!
echo Looking for python source code...
if exist venv\Scripts\activate.bat call venv\Scripts\activate
python -m backend.main
)

if exist .update_ready (
echo.
echo [UPDATE] Installing update...
timeout /t 2 >nul

xcopy update_stage\* . /E /Y /H

rmdir /s /q update_stage
del .update_ready

echo [UPDATE] Done! Restarting...
timeout /t 2 >nul
goto loop


)

echo [HomeHub] Application stopped.
pause