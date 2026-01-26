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
$TRACKER_SCRIPT = Join-Path $SCRIPT_DIR "run_amazon_tracker.ps1"
$TASK_NAME_PREFIX = "Amazon Price Tracker"

# Check if tracker script exists
if (-not (Test-Path $TRACKER_SCRIPT)) {
    Write-Error "Tracker script not found: $TRACKER_SCRIPT"
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

Write-Host ""
Write-Host "Creating scheduled tasks..." -ForegroundColor Cyan

$successCount = 0
$failCount = 0

foreach ($schedule in $schedules) {
    $taskName = "$TASK_NAME_PREFIX - $($schedule.Time)"
    
    try {
        # Remove existing task if it exists
        $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Host "  Removed existing task: $taskName" -ForegroundColor Yellow
        }
        
        # Create action
        $action = New-ScheduledTaskAction `
            -Execute "PowerShell.exe" `
            -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$TRACKER_SCRIPT`"" `
            -WorkingDirectory $SCRIPT_DIR
        
        # Create trigger (daily at specified time)
        $trigger = New-ScheduledTaskTrigger -Daily -At $schedule.Time
        
        # Create settings
        $settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable `
            -RunOnlyIfNetworkAvailable `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
        
        # Create principal (run with highest privileges)
        $principal = New-ScheduledTaskPrincipal `
            -UserId $currentUser `
            -LogonType S4U `
            -RunLevel Highest
        
        # Register task
        Register-ScheduledTask `
            -TaskName $taskName `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Principal $principal `
            -Description "Amazon Price Tracker - $($schedule.Description)" | Out-Null
        
        Write-Host "  ✓ Created: $taskName" -ForegroundColor Green
        $successCount++
        
    } catch {
        Write-Host "  ✗ Failed: $taskName - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Created: $successCount tasks" -ForegroundColor Green
Write-Host "  Failed:  $failCount tasks" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run 'setup_telegram_env.bat' to configure Telegram credentials" -ForegroundColor White
Write-Host "  2. Test manually by running 'run_tracker.bat'" -ForegroundColor White
Write-Host "  3. Check Task Scheduler to verify tasks are created" -ForegroundColor White
Write-Host "  4. Monitor 'tracker_logs.txt' for execution logs" -ForegroundColor White
Write-Host ""
Write-Host "To view tasks: Open Task Scheduler > Task Scheduler Library" -ForegroundColor Cyan
Write-Host "To disable a task: Right-click task > Disable" -ForegroundColor Cyan
Write-Host "To delete all tasks: Run this script again or delete manually" -ForegroundColor Cyan
Write-Host ""

pause
