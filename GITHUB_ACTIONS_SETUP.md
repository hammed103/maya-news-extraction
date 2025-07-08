# GitHub Actions Setup for Maya News Scraper

This guide will help you set up automated daily news scraping using GitHub Actions.

## Prerequisites

1. GitHub repository with your code
2. OpenAI API key
3. Google Service Account credentials JSON file

## Setup Steps

### 1. Repository Setup

Make sure your repository contains:
- All Python scripts
- `requirements.txt`
- `.github/workflows/daily-news-scraper.yml` (created by this setup)

### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these repository secrets:

#### Required Secrets:

**OPENAI_API_KEY**
- Your OpenAI API key
- Example: `sk-proj-...`

**GOOGLE_CREDENTIALS_JSON**
- Your Google Service Account credentials as JSON
- Copy the entire contents of your `credentials.json` file
- Should look like:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### 3. Workflow Configuration

The workflow is configured to:
- Run daily at 6:00 AM UTC
- Can be triggered manually from the Actions tab
- Installs dependencies
- Runs the news scraper
- Saves logs and results as artifacts

### 4. Customize Schedule

To change the schedule, edit `.github/workflows/daily-news-scraper.yml`:

```yaml
schedule:
  # Run daily at 6:00 AM UTC
  - cron: '0 6 * * *'
```

Common cron schedules:
- `'0 6 * * *'` - Daily at 6:00 AM UTC
- `'0 12 * * *'` - Daily at 12:00 PM UTC
- `'0 6 * * 1-5'` - Weekdays only at 6:00 AM UTC
- `'0 6,18 * * *'` - Twice daily at 6:00 AM and 6:00 PM UTC

### 5. Test the Setup

1. Push your code to GitHub
2. Go to Actions tab in your repository
3. Click on "Daily News Scraper" workflow
4. Click "Run workflow" to test manually
5. Monitor the workflow execution

### 6. Monitor Results

#### Viewing Logs:
1. Go to Actions tab
2. Click on a workflow run
3. Click on the "scrape-news" job
4. Expand the steps to see detailed logs

#### Downloading Artifacts:
1. After a workflow completes, scroll down to "Artifacts"
2. Download "scraper-logs" to get:
   - Log files (*.log)
   - CSV results (ground_news_results_*.csv)
   - Generated scripts (explainer_script_*.txt)

### 7. Troubleshooting

#### Common Issues:

**Secrets not working:**
- Ensure secret names match exactly (case-sensitive)
- Check that JSON is properly formatted
- Verify API key is valid

**Workflow not running:**
- Check that the workflow file is in `.github/workflows/`
- Verify cron syntax is correct
- Ensure repository has Actions enabled

**Python errors:**
- Check requirements.txt includes all dependencies
- Verify Python version compatibility (using 3.11)

**Google Sheets access:**
- Ensure service account has access to your spreadsheet
- Check that credentials JSON is complete and valid

#### Debugging Steps:

1. **Test locally first:**
   ```bash
   python ground_news_scraper.py
   ```

2. **Check workflow syntax:**
   - GitHub will show syntax errors in the Actions tab

3. **Review logs:**
   - Always check the detailed logs in the Actions tab

4. **Test with manual trigger:**
   - Use "Run workflow" button to test without waiting for schedule

### 8. Security Considerations

- Never commit credentials.json to your repository
- Use GitHub Secrets for all sensitive information
- Regularly rotate your API keys
- Monitor your OpenAI usage to avoid unexpected charges

### 9. Cost Considerations

- GitHub Actions provides free minutes for public repositories
- Private repositories have limited free minutes
- Monitor your OpenAI API usage
- Consider using workflow conditions to prevent unnecessary runs

### 10. Advanced Configuration

#### Multiple Schedules:
```yaml
on:
  schedule:
    - cron: '0 6 * * *'   # Morning run
    - cron: '0 18 * * *'  # Evening run
```

#### Conditional Execution:
```yaml
- name: Run news scraper
  if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: python ground_news_scraper.py
```

#### Notifications:
Add Slack/email notifications for failures by adding notification steps to the workflow.

## Support

If you encounter issues:
1. Check the GitHub Actions documentation
2. Review the workflow logs carefully
3. Test your scripts locally first
4. Verify all secrets are properly configured
