# 🕐 Schedule Configuration Guide

This guide explains how to change when your Maya News Scraper runs automatically.

## Quick Schedule Changes

### Method 1: Edit Workflow File (Easiest)

1. **Go to your repository** on GitHub
2. **Navigate to** `.github/workflows/daily-news-scraper.yml`
3. **Click the pencil icon** (✏️ Edit this file)
4. **Find line with `cron:`** (around line 13)
5. **Replace the time** with your preferred schedule
6. **Scroll down and click "Commit changes"**

### Current Schedule
```yaml
- cron: '0 6 * * *'  # 6:00 AM UTC daily
```

## 📅 Common Schedule Examples

Copy and paste any of these to replace the cron line:

### Daily Schedules
```yaml
# Morning schedules
- cron: '0 6 * * *'   # 6:00 AM UTC
- cron: '0 7 * * *'   # 7:00 AM UTC  
- cron: '0 8 * * *'   # 8:00 AM UTC
- cron: '30 8 * * *'  # 8:30 AM UTC

# Afternoon schedules  
- cron: '0 12 * * *'  # 12:00 PM UTC
- cron: '0 14 * * *'  # 2:00 PM UTC
- cron: '0 16 * * *'  # 4:00 PM UTC

# Evening schedules
- cron: '0 18 * * *'  # 6:00 PM UTC
- cron: '0 20 * * *'  # 8:00 PM UTC
- cron: '0 22 * * *'  # 10:00 PM UTC
```

### Weekdays Only
```yaml
- cron: '0 6 * * 1-5'   # 6:00 AM UTC, Monday-Friday
- cron: '0 8 * * 1-5'   # 8:00 AM UTC, Monday-Friday
- cron: '0 12 * * 1-5'  # 12:00 PM UTC, Monday-Friday
```

### Multiple Times Per Day
```yaml
- cron: '0 6,18 * * *'    # 6:00 AM and 6:00 PM UTC
- cron: '0 8,12,16 * * *' # 8:00 AM, 12:00 PM, and 4:00 PM UTC
- cron: '0 */6 * * *'     # Every 6 hours
- cron: '0 */12 * * *'    # Every 12 hours
```

### Weekend Only
```yaml
- cron: '0 10 * * 0,6'  # 10:00 AM UTC on Saturday and Sunday
```

## 🌍 Timezone Considerations

**Important**: All times are in UTC (Coordinated Universal Time).

### Convert Your Local Time to UTC:

| Your Timezone | Local Time | UTC Time | Cron Expression |
|---------------|------------|----------|-----------------|
| EST (UTC-5)   | 8:00 AM    | 1:00 PM  | `'0 13 * * *'`  |
| PST (UTC-8)   | 8:00 AM    | 4:00 PM  | `'0 16 * * *'`  |
| GMT (UTC+0)   | 8:00 AM    | 8:00 AM  | `'0 8 * * *'`   |
| CET (UTC+1)   | 8:00 AM    | 7:00 AM  | `'0 7 * * *'`   |
| JST (UTC+9)   | 8:00 AM    | 11:00 PM | `'0 23 * * *'`  |

### Quick Timezone Calculator:
- **EST/EDT**: Add 5 hours (4 during daylight saving)
- **PST/PDT**: Add 8 hours (7 during daylight saving)  
- **GMT/BST**: Same as UTC (subtract 1 during daylight saving)
- **CET/CEST**: Subtract 1 hour (2 during daylight saving)

## 🔧 Cron Format Explained

```
┌───────────── minute (0 - 59)
│ ┌─────────── hour (0 - 23)
│ │ ┌───────── day of month (1 - 31)
│ │ │ ┌─────── month (1 - 12)
│ │ │ │ ┌───── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

### Special Characters:
- `*` = any value
- `,` = list separator (e.g., `1,3,5`)
- `-` = range (e.g., `1-5` for Monday-Friday)
- `/` = step values (e.g., `*/2` for every 2 hours)

## 🧪 Testing Your Schedule

After changing the schedule:

1. **Save the changes** to the workflow file
2. **Go to Actions tab** in your repository
3. **Click "Daily News Scraper"**
4. **Click "Run workflow"** to test manually
5. **Check the next scheduled run** in the Actions tab

## 📱 Manual Triggers

Your scraper can always be run manually:
1. Go to **Actions** tab
2. Click **"Daily News Scraper"**
3. Click **"Run workflow"** → **"Run workflow"**

## 🚨 Important Notes

- Changes take effect immediately after committing
- GitHub Actions may have a few minutes delay
- Free GitHub accounts have limited action minutes
- The scraper will create new Google Sheets entries each run

## 📞 Need Help?

If you need a custom schedule not covered here:
1. Use an online cron generator (search "cron generator")
2. Test your cron expression before committing
3. Remember to convert your local time to UTC

## 🔄 Reverting Changes

To go back to the original schedule:
```yaml
- cron: '0 6 * * *'  # 6:00 AM UTC daily
```
