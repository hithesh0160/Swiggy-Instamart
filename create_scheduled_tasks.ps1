# Create Windows Scheduled Tasks for Amazon Price Tracker
# Run this script as Administrator to create all scheduled tasks

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script requires Administrator privileges!"
    Write-Host "Please run PowerShell as Administrator and try again."
    pause
    exit
}

# Configuration
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$TRACKER_BAT = Join-Path $SCRIPT_DIR "run_silent.bat"
$TASK_NAME_PREFIX = "Amazon Tracker" # Shortened to avoid potential length issues

# Check if tracker bat exists
if (-not (Test-Path $TRACKER_BAT)) {
    Write-Error "Tracker bridge not found: $TRACKER_BAT"
    pause
    exit 1
}

# Get current user
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Amazon Price Tracker - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will create 6 scheduled tasks to run the tracker daily:" -ForegroundColor Yellow
Write-Host "  - 6:00 AM  (Early morning deals)" -ForegroundColor White
Write-Host "  - 10:00 AM (Mid-morning refresh)" -ForegroundColor White
Write-Host "  - 2:00 PM  (Afternoon deals)" -ForegroundColor White
Write-Host "  - 6:00 PM  (Evening peak)" -ForegroundColor White
Write-Host "  - 9:00 PM  (Prime time)" -ForegroundColor White
Write-Host "  - 11:30 PM (Late night clearance)" -ForegroundColor White
Write-Host ""
Write-Host "Tasks will run as: $currentUser" -ForegroundColor Green
Write-Host ""

$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Cancelled by user"
    exit
}

# Define schedule times (24-hour format)
$schedules = @(
    @{Time = "06:00"; Description = "Early morning deals"},
    @{Time = "10:00"; Description = "Mid-morning refresh"},
    @{Time = "14:00"; Description = "Afternoon deals"},
    @{Time = "18:00"; Description = "Evening peak"},
    @{Time = "21:00"; Description = "Prime time"},
    @{Time = "23:30"; Description = "Late night clearance"}
)

# Configuration for the bridge
$TEMP_BAT = Join-Path $SCRIPT_DIR "temp_setup_tasks.bat"

Write-Host "Generating temporary setup script..." -ForegroundColor Cyan

# Start building the batch file content
$batContent = @(
    "@echo off",
    "echo Creating Amazon Tracker scheduled tasks...",
    "echo."
)

foreach ($schedule in $schedules) {
    $taskName = "$TASK_NAME_PREFIX - $($schedule.Time)"
    
    # In Batch/CMD, quoting a path with spaces is simple: "path"
    # We use schtasks.exe directly in the batch file
    $batContent += "echo   Creating: $taskName"
    $batContent += "schtasks /Create /TN `"$taskName`" /TR `"$TRACKER_BAT`" /SC DAILY /ST $($schedule.Time):00 /RL HIGHEST /F >nul"
    
    # Check if last command succeeded in batch
    $batContent += "if %errorlevel% equ 0 (echo     [OK] Success) else (echo     [FAIL] Failed with error code %errorlevel%)"
    $batContent += "echo."
}

$batContent += "pause"

# Write the batch file with UTF8 encoding (no BOM) for best CMD compatibility
$batContent | Out-File -FilePath $TEMP_BAT -Encoding ascii

Write-Host "Generation complete." -ForegroundColor Green
Write-Host ""
Write-Host "============================" -ForegroundColor Yellow
Write-Host "MANUAL STEP REQUIRED" -ForegroundColor Yellow
Write-Host "============================" -ForegroundColor Yellow
Write-Host "To ensure the tasks are created with the correct permissions:"
Write-Host "1. I have created a file: $TEMP_BAT"
Write-Host "2. Please RIGHT-CLICK that file and select 'Run as Administrator'."
Write-Host "3. After it finishes, you can delete both '$TEMP_BAT' and 'run_task_setup.bat'."
Write-Host ""

pause
