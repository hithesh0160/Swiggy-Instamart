@echo off
REM Amazon Price Tracker - Quick Run Batch File
REM Double-click this file to run the tracker manually

echo ========================================
echo Amazon Price Tracker
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if PowerShell script exists
if not exist "run_amazon_tracker.ps1" (
    echo ERROR: run_amazon_tracker.ps1 not found!
    pause
    exit /b 1
)

REM Run PowerShell script
echo Running tracker...
echo.
powershell.exe -ExecutionPolicy Bypass -File "run_amazon_tracker.ps1"

echo.
echo ========================================
echo Tracker execution completed
echo Check tracker_logs.txt for details
echo ========================================
echo.

pause
