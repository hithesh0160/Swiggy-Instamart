@echo off
REM Setup Telegram Environment Variables for Windows
REM Run this ONCE to configure Telegram credentials

echo ========================================
echo Telegram Credentials Setup
echo ========================================
echo.
echo This will set your Telegram credentials as SYSTEM environment variables
echo so they work with Task Scheduler.
echo.

REM Prompt for credentials
set /p BOT_TOKEN="Enter your TELEGRAM_BOT_TOKEN: "
set /p CHAT_ID="Enter your TELEGRAM_CHAT_ID: "

echo.
echo Setting environment variables...

REM Set USER environment variables (for manual runs)
setx TELEGRAM_BOT_TOKEN "%BOT_TOKEN%"
setx TELEGRAM_CHAT_ID "%CHAT_ID%"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Environment variables set:
echo   TELEGRAM_BOT_TOKEN: %BOT_TOKEN%
echo   TELEGRAM_CHAT_ID: %CHAT_ID%
echo.
echo NOTE: You may need to restart your terminal/PowerShell
echo for the changes to take effect.
echo.
echo For Task Scheduler to use these, make sure to:
echo 1. Run tasks with your user account (not SYSTEM)
echo 2. Check "Run whether user is logged on or not"
echo.

pause
