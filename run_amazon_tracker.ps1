# Amazon Price Tracker - Windows Task Scheduler Script
# This script runs the Amazon tracker and handles errors

# Configuration
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_SCRIPT = Join-Path $SCRIPT_DIR "amazon_price_tracker.py"
$LOG_FILE = Join-Path $SCRIPT_DIR "tracker_logs.txt"
$MAX_LOG_SIZE = 5MB

# Function to write logs
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# Rotate log file if too large
if (Test-Path $LOG_FILE) {
    $logSize = (Get-Item $LOG_FILE).Length
    if ($logSize -gt $MAX_LOG_SIZE) {
        $backupLog = Join-Path $SCRIPT_DIR "tracker_logs_old.txt"
        Move-Item -Path $LOG_FILE -Destination $backupLog -Force
        Write-Log "Log file rotated (was $([math]::Round($logSize/1MB, 2)) MB)"
    }
}

# Start tracking
Write-Log "========================================="
Write-Log "Starting Amazon Price Tracker"
Write-Log "========================================="

# Change to script directory
Set-Location $SCRIPT_DIR
Write-Log "Working directory: $SCRIPT_DIR"

# Check if Python script exists
if (-not (Test-Path $PYTHON_SCRIPT)) {
    Write-Host "ERROR: Python script not found: $PYTHON_SCRIPT" -ForegroundColor Red
    Write-Log "ERROR: Python script not found: $PYTHON_SCRIPT"
    exit 1
}

# Check for Telegram credentials
if (-not $env:TELEGRAM_BOT_TOKEN -or -not $env:TELEGRAM_CHAT_ID) {
    Write-Host "WARNING: Telegram credentials not set in environment variables" -ForegroundColor Yellow
    Write-Host "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID for notifications" -ForegroundColor Yellow
    Write-Log "WARNING: Telegram credentials not set in environment variables"
}

# Run the tracker - output directly to console
try {
    Write-Host "Executing: python $PYTHON_SCRIPT" -ForegroundColor Cyan
    Write-Log "Executing: python $PYTHON_SCRIPT"
    
    # Run Python script with output shown directly in console
    # Also capture to log file using Tee-Object
    & python $PYTHON_SCRIPT 2>&1 | Tee-Object -FilePath $LOG_FILE -Append
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "`nSUCCESS: Tracker completed successfully" -ForegroundColor Green
        Write-Log "SUCCESS: Tracker completed successfully"
    } else {
        Write-Host "`nERROR: Tracker failed with exit code $exitCode" -ForegroundColor Red
        Write-Log "ERROR: Tracker failed with exit code $exitCode"
    }
    
} catch {
    Write-Host "EXCEPTION: $($_.Exception.Message)" -ForegroundColor Red
    Write-Log "EXCEPTION: $($_.Exception.Message)"
    Write-Log "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

Write-Log "========================================="
Write-Log "Tracker execution completed"
Write-Log "========================================="

exit $exitCode
