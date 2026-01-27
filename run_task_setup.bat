@echo off
:: Amazon Price Tracker - Task Setup Wrapper
:: This file runs the PowerShell script to create scheduled tasks with Administrator privileges

echo ========================================
echo Amazon Price Tracker - Task Setup
echo ========================================
echo.

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges.
) else (
    echo [ERROR] This script requires Administrator privileges.
    echo Please right-click this file and select "Run as administrator".
    pause
    exit /b 1
)

:: Change to script directory
cd /d "%~dp0"

:: Check if PowerShell script exists
if not exist "create_scheduled_tasks.ps1" (
    echo [ERROR] create_scheduled_tasks.ps1 not found!
    pause
    exit /b 1
)

echo Starting Task Scheduler Setup...
echo.

:: Run PowerShell script with Bypass policy
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "create_scheduled_tasks.ps1"

echo.
echo ========================================
echo Process finished.
echo ========================================
echo.

pause
