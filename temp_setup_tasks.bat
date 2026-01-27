@echo off
echo Creating Amazon Tracker scheduled tasks...
echo.
echo   Creating: Amazon Tracker - 06:00
schtasks /Create /TN "Amazon Tracker - 06:00" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 06:00:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
echo   Creating: Amazon Tracker - 10:00
schtasks /Create /TN "Amazon Tracker - 10:00" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 10:00:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
echo   Creating: Amazon Tracker - 14:00
schtasks /Create /TN "Amazon Tracker - 14:00" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 14:00:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
echo   Creating: Amazon Tracker - 18:00
schtasks /Create /TN "Amazon Tracker - 18:00" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 18:00:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
echo   Creating: Amazon Tracker - 21:00
schtasks /Create /TN "Amazon Tracker - 21:00" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 21:00:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
echo   Creating: Amazon Tracker - 23:30
schtasks /Create /TN "Amazon Tracker - 23:30" /TR "D:\Swiggy Instamart\run_silent.bat" /SC DAILY /ST 23:30:00 /RL HIGHEST /F >nul
if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)
echo.
pause
