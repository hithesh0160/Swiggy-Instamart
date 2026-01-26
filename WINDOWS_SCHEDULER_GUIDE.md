# Windows Task Scheduler Setup Guide

Complete guide to set up automated Amazon price tracking on Windows.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Telegram Credentials

1. **Double-click** `setup_telegram_env.bat`
2. Enter your Telegram bot token
3. Enter your Telegram chat ID
4. Press Enter

✅ This sets environment variables so Telegram notifications work.

### Step 2: Create Scheduled Tasks

1. **Right-click** `create_scheduled_tasks.ps1`
2. Select **"Run with PowerShell"** (as Administrator)
3. Press `Y` to confirm
4. Wait for tasks to be created

✅ This creates 6 scheduled tasks to run the tracker automatically.

### Step 3: Test Manual Run

1. **Double-click** `run_tracker.bat`
2. Wait for execution to complete
3. Check `tracker_logs.txt` for results
4. Check Telegram for notification

✅ If this works, automated runs will work too!

---

## 📅 Scheduled Run Times

The tracker will run **6 times per day**:

| Time | Purpose | Expected Deals |
|------|---------|----------------|
| **6:00 AM** | Early morning | Lightning Deals start |
| **10:00 AM** | Mid-morning | New deals added |
| **2:00 PM** | Afternoon | Lunch specials |
| **6:00 PM** | Evening peak | Prime time deals |
| **9:00 PM** | Prime time | Flash sales |
| **11:30 PM** | Late night | End-of-day clearance |

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `run_amazon_tracker.ps1` | Main execution script with logging |
| `run_tracker.bat` | Quick manual run (double-click) |
| `setup_telegram_env.bat` | One-time Telegram setup |
| `create_scheduled_tasks.ps1` | Creates all 6 scheduled tasks |
| `tracker_logs.txt` | Execution logs (auto-rotates at 5MB) |
| `tracker_logs_old.txt` | Backup of rotated logs |

---

## 🔧 Configuration

### Telegram Credentials

**Option 1: Using setup script (Recommended)**
```batch
# Run this once
setup_telegram_env.bat
```

**Option 2: Manual setup**
```powershell
# Set environment variables manually
setx TELEGRAM_BOT_TOKEN "your_bot_token_here"
setx TELEGRAM_CHAT_ID "your_chat_id_here"
```

**Option 3: Edit Python script directly**
Edit `amazon_price_tracker.py` and set:
```python
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

### Modify Schedule Times

Edit `create_scheduled_tasks.ps1` and change the `$schedules` array:

```powershell
$schedules = @(
    @{Time = "06:00"; Description = "Early morning deals"},
    @{Time = "10:00"; Description = "Mid-morning refresh"},
    # Add or modify times here
)
```

Then run the script again to recreate tasks.

---

## 📊 Monitoring

### View Logs

**Real-time monitoring:**
```powershell
Get-Content tracker_logs.txt -Wait -Tail 20
```

**View last 50 lines:**
```powershell
Get-Content tracker_logs.txt -Tail 50
```

**Open in Notepad:**
```batch
notepad tracker_logs.txt
```

### Check Task Status

**PowerShell:**
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon Price Tracker*"}
```

**Task Scheduler GUI:**
1. Press `Win + R`
2. Type `taskschd.msc`
3. Press Enter
4. Look for "Amazon Price Tracker" tasks

### View Task History

1. Open Task Scheduler (`taskschd.msc`)
2. Find task in list
3. Click on "History" tab at bottom
4. View execution results

---

## 🛠️ Troubleshooting

### Tasks Not Running

**Check if tasks exist:**
```powershell
Get-ScheduledTask -TaskName "Amazon Price Tracker*"
```

**Manually trigger a task:**
```powershell
Start-ScheduledTask -TaskName "Amazon Price Tracker - 06:00"
```

**Check last run result:**
```powershell
Get-ScheduledTask -TaskName "Amazon Price Tracker - 06:00" | Get-ScheduledTaskInfo
```

### No Telegram Notifications

**Verify environment variables:**
```powershell
echo $env:TELEGRAM_BOT_TOKEN
echo $env:TELEGRAM_CHAT_ID
```

If empty, run `setup_telegram_env.bat` again.

**Test Telegram manually:**
Edit `amazon_price_tracker.py` and add at the top:
```python
# Test Telegram
import os
print(f"Bot Token: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"Chat ID: {os.getenv('TELEGRAM_CHAT_ID')}")
```

### Script Errors

**Check Python is installed:**
```powershell
python --version
```

**Check dependencies:**
```powershell
pip list | findstr "playwright requests"
```

**Install missing dependencies:**
```powershell
pip install playwright requests beautifulsoup4 lxml
python -m playwright install chromium
```

### PC Must Be On

**Important:** Windows Task Scheduler requires:
- ✅ PC is powered on (not shut down)
- ✅ PC is awake (not sleeping/hibernating)
- ⚠️ PC can be locked (tasks will still run)

**To prevent sleep during scheduled runs:**
1. Open Power Options
2. Set "Put computer to sleep" to "Never" (or after midnight)
3. Or use "Wake computer to run this task" in task settings

---

## 🔄 Management Commands

### Delete All Tasks

**PowerShell (as Administrator):**
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon Price Tracker*"} | Unregister-ScheduledTask -Confirm:$false
```

### Disable All Tasks

```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon Price Tracker*"} | Disable-ScheduledTask
```

### Enable All Tasks

```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon Price Tracker*"} | Enable-ScheduledTask
```

### Run All Tasks Now (Testing)

```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon Price Tracker*"} | Start-ScheduledTask
```

---

## 📈 Expected Behavior

### First Run
- Creates `price_history.json`
- All deals marked as NEW
- Telegram alert with all deals

### Subsequent Runs
- Compares against price history
- Only alerts on:
  - New deals (not seen before)
  - Price drops >20%
  - Pricing errors (>70% discount)

### Log File
- Rotates automatically at 5MB
- Old logs saved to `tracker_logs_old.txt`
- Contains timestamps, errors, and execution details

---

## 🎯 Best Practices

1. **Test First:** Run `run_tracker.bat` manually before relying on scheduled tasks
2. **Monitor Logs:** Check `tracker_logs.txt` daily for first week
3. **Keep PC On:** Ensure PC is on during scheduled times
4. **Update Regularly:** Pull latest code from GitHub occasionally
5. **Backup Data:** Keep `price_history.json` backed up

---

## 🔐 Security Notes

- Environment variables are stored per-user (secure)
- Tasks run with your user account (not SYSTEM)
- Telegram tokens are NOT stored in code
- Logs don't contain sensitive data

---

## 📞 Support

### Check Logs First
```powershell
Get-Content tracker_logs.txt -Tail 50
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Tasks not running | Check PC is on and awake |
| No Telegram alerts | Run `setup_telegram_env.bat` |
| Python errors | Reinstall dependencies |
| Permission errors | Run PowerShell as Administrator |

---

## 🎉 Success Indicators

✅ **Setup is working if:**
- Tasks appear in Task Scheduler
- `tracker_logs.txt` shows successful runs
- Telegram receives notifications
- `price_history.json` is updated
- `amazon_deals.json` contains deals

---

**Last Updated:** January 26, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
