@echo off
:: Amazon Price Tracker - Silent Execution Bridge
:: This file is used by Task Scheduler to run the tracker without a persistent window.

:: Change to the directory where this batch file is located
cd /d "%~dp0"

:: Run the PowerShell script
:: Using full path to PowerShell and specific parameters for maximum reliability
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "run_amazon_tracker.ps1"
