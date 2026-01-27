# Manual Setup Guide

Since the automatic script was having trouble with your specific system configuration, here is the robust manual way to set up the schedule.

## 1. Prepare the Script
Ensure `run_silent.bat` is in your folder:
`d:\Swiggy Instamart\run_silent.bat`

## 2. Open Task Scheduler
1. Press `Win + R`
2. Type `taskschd.msc` and press Enter.

## 3. Create the Task
1. In the right pane, click **Create Basic Task...**
2. **Name**: `Amazon Tracker`
3. **Trigger**: Select **Daily**.
4. **Time**: Set to **08:30:00**. Recur every **1** days.
5. **Action**: **Start a program**.
6. **Program/script**: Browse and select `d:\Swiggy Instamart\run_silent.bat`
   - **IMPORTANT**: In "Start in (optional)", enter: `d:\Swiggy Instamart\`
7. Click **Finish**.

## 4. Add Additional Times (Optional)
To add 11:30 AM, 2:00 PM, etc. to the *same* task:
1. Double-click the `Amazon Tracker` task you just created in the list.
2. Go to the **Triggers** tab.
3. Click **New...**
4. Select **Daily** and set the time to **11:30:00**.
5. Repeat for other times (14:00, 18:00, 21:00, 23:30).

## 5. Enable "Run whether user is logged on or not" (Recommended)
1. In the task properties (General tab).
2. Select **Run whether user is logged on or not**.
3. Check **Run with highest privileges**.
4. Click OK (System will ask for your password).
