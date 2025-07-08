# Maya News Extraction - Configuration Management

This system allows you to manage keywords and prompts for the Maya News Extraction automation directly through Google Sheets, making it easy to update tracking topics and AI prompts without modifying code.

## 🚀 Quick Start

### 1. Initial Setup
Run the setup script to create the configuration sheets:
```bash
python setup_configuration.py
```

This will create two new tabs in your "Maya News Extraction" Google Sheet:
- **Keywords**: Manages search keywords by category
- **Prompts**: Manages OpenAI prompts for different functions

### 2. Test the Configuration
Verify everything is working:
```bash
python test_configuration.py
```

## 📋 Keywords Sheet

The Keywords sheet has three columns:

| Column | Description | Example |
|--------|-------------|---------|
| Category | The category name | "Press & Information Freedom" |
| Keyword | The search term | "press freedom" |
| Active | TRUE/FALSE to enable/disable | "TRUE" |

### Managing Keywords

**To track a new story (like the budget bill):**
1. Open the Keywords sheet in Google Sheets
2. Add new rows with relevant keywords:
   ```
   Category: Budget & Fiscal Policy
   Keyword: budget bill
   Active: TRUE
   
   Category: Budget & Fiscal Policy  
   Keyword: government funding
   Active: TRUE
   
   Category: Budget & Fiscal Policy
   Keyword: spending bill
   Active: TRUE
   ```

**To stop tracking a story:**
1. Find the keywords you want to disable
2. Change "Active" from "TRUE" to "FALSE"
3. The scrapers will skip these keywords on the next run

**To temporarily disable a category:**
1. Set all keywords in that category to "Active: FALSE"

## 💬 Prompts Sheet

The Prompts sheet has three columns:

| Column | Description |
|--------|-------------|
| Prompt Name | Identifier for the prompt |
| Prompt Text | The full OpenAI prompt |
| Active | TRUE/FALSE to enable/disable |

### Current Prompts

1. **Explainer Script**: Generates 60-second democracy briefings
2. **One Sheet Briefing**: Creates comprehensive news summaries  
3. **US Article Filter**: Determines if articles are US-focused

### Updating Prompts

**To modify the explainer script tone:**
1. Open the Prompts sheet
2. Find "Explainer Script" row
3. Edit the "Prompt Text" column
4. Changes take effect on next scraper run

**Example modification** - to focus more on specific issues:
```
You are a U.S.-based political journalist creating a 60-second daily briefing focusing specifically on voting rights and election integrity...
```

## 🔧 How It Works

### Automatic Loading
Both scrapers (`ground_news_scraper.py` and `nick.py`) now:
1. Load keywords from the Keywords sheet at startup
2. Load prompts from the Prompts sheet when needed
3. Fall back to hardcoded defaults if sheets are unavailable

### Real-time Updates
- Changes to Google Sheets take effect on the next scraper run
- No code changes or restarts required
- Keywords and prompts are loaded fresh each time

## 📊 Monitoring

### Logs
Check the scraper logs for configuration loading status:
```
INFO - Loaded 11 categories from Keywords sheet
INFO - Loaded 3 prompts from Prompts sheet
```

### Fallback Behavior
If Google Sheets is unavailable:
```
WARNING - Keywords sheet not found, using fallback categories
WARNING - Prompts sheet not found, using fallback prompts
```

## 🎯 Use Cases

### Tracking Breaking News
When a major story breaks (like the budget bill):
1. Add relevant keywords to the Keywords sheet
2. Set them to "Active: TRUE"
3. Run the scraper to start collecting articles

### Seasonal Adjustments
For election periods:
1. Temporarily boost election-related keywords
2. Adjust prompts to focus more on election integrity
3. Disable less relevant categories

### Content Tuning
To improve AI outputs:
1. Modify prompts based on output quality
2. Test different prompt variations
3. A/B test by temporarily switching prompts

## 🛠️ Troubleshooting

### Common Issues

**"Failed to load keywords"**
- Check credentials.json file exists
- Verify Google Sheets API access
- Ensure "Maya News Extraction" sheet exists

**"Keywords sheet not found"**
- Run `python setup_keywords_sheet.py`
- Check sheet name is exactly "Keywords"

**"Prompts sheet not found"**
- Run `python setup_prompts_sheet.py`  
- Check sheet name is exactly "Prompts"

### Testing
Always test changes with:
```bash
python test_configuration.py
```

## 📝 Best Practices

1. **Backup**: Keep a copy of working configurations
2. **Testing**: Test prompt changes with small datasets first
3. **Documentation**: Add comments in unused columns for context
4. **Gradual Changes**: Make incremental adjustments rather than major overhauls
5. **Monitoring**: Watch logs for any loading errors

## 🔄 Migration Notes

The system maintains backward compatibility:
- If Google Sheets are unavailable, fallback keywords/prompts are used
- Original hardcoded configurations have been removed from the code
- All configuration is now centralized in Google Sheets

This makes the system much more flexible and user-friendly for tracking evolving news stories!
