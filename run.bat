@echo off
setlocal
title HomeHub Launcher
cd /d "%~dp0"

:loop
cls
echo [HomeHub] Checking environment...

if exist .update_ready (
    goto update_process
)

echo [HomeHub] Starting Application...
if exist HomeHub.exe (
    start "" /WAIT HomeHub.exe
) else (
    echo [ERROR] HomeHub.exe not found!
    echo Trying to launch from source...
    if exist venv\Scripts\activate.bat call venv\Scripts\activate
    python -m backend.main
)

if exist .update_ready (
    goto update_process
)

echo.
echo [HomeHub] Application closed.
goto end

:update_process
echo.
echo ==========================================
echo      INSTALLING UPDATE - PLEASE WAIT
echo ==========================================
echo.
timeout /t 2 >nul

taskkill /F /IM HomeHub.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

if exist update_stage (
    echo Copying files...
    xcopy update_stage\* . /E /Y /H /Q
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to copy update files!
        pause
        goto loop
    )
    
    echo Cleaning up...
    rmdir /s /q update_stage
    del .update_ready
    
    echo [SUCCESS] Update installed!
    timeout /t 2 >nul
    goto loop
) else (
    echo [ERROR] Update folder not found!
    del .update_ready
    goto loop
)

:end