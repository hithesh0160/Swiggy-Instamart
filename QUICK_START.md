# Amazon Tracker - Quick Setup (3 Steps)

## ⚡ Setup in 3 Minutes

### Step 1: Setup Telegram (One-time)
```
Double-click: setup_telegram_env.bat
Enter your bot token and chat ID
```

### Step 2: Create Scheduled Tasks (One-time)
```
Right-click: create_scheduled_tasks.ps1
Select "Run with PowerShell" (as Administrator)
Press Y to confirm
```

### Step 3: Test It Works
```
Double-click: run_tracker.bat
Check Telegram for notification
```

✅ **Done!** Tracker will now run automatically 6 times per day.

---

## 📅 Schedule

| Time | Purpose |
|------|---------|
| 6:00 AM | Early morning deals |
| 10:00 AM | Mid-morning refresh |
| 2:00 PM | Afternoon deals |
| 6:00 PM | Evening peak |
| 9:00 PM | Prime time |
| 11:30 PM | Late night clearance |

---

## 📁 Files

- **run_tracker.bat** - Manual run (double-click)
- **tracker_logs.txt** - View execution logs
- **WINDOWS_SCHEDULER_GUIDE.md** - Full documentation

---

## 🔧 Quick Commands

**Run manually (see output in same window):**
```
Double-click: run_tracker.bat
```

**View logs:**
```powershell
notepad tracker_logs.txt
```

**Check scheduled tasks:**
```powershell
Get-ScheduledTask | Where-Object {$_.TaskName -like "Amazon*"}
```

**Run task now:**
```powershell
Start-ScheduledTask -TaskName "Amazon Price Tracker - 06:00"
```

**Check task status:**
```
Press Win+R, type: taskschd.msc
Find "Amazon Price Tracker" tasks
```

---

## ⚠️ Important

- Keep PC on during scheduled times
- PC can be locked (tasks still run)
- Logs auto-rotate at 5MB
- Only NEW deals trigger Telegram alerts

---

**Need help?** See WINDOWS_SCHEDULER_GUIDE.md
