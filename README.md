# Maya News Extraction System

An automated news scraping and analysis system that collects U.S. political news articles and generates daily briefings focused on American democracy impacts.

## 🚀 Features

- **Automated News Scraping**: Collects articles from Ground News based on configurable keywords
- **AI-Powered Analysis**: Uses OpenAI GPT-4 to filter and summarize articles
- **Democracy Focus**: Specifically targets news with impacts on American democracy
- **Daily Briefings**: Generates 60-second explainer scripts and comprehensive one-sheet briefings
- **Google Sheets Integration**: Stores all data in organized Google Sheets
- **Automated Scheduling**: Runs daily via GitHub Actions

## 📋 Components

### Main Scripts
- `ground_news_scraper.py` - Main scraper that collects articles and generates briefings
- `explainer_script_generator.py` - Standalone script for generating explainer scripts
- `setup_configuration.py` - Sets up Google Sheets configuration system

### Configuration
- Keywords and categories stored in Google Sheets "Keywords" tab
- AI prompts stored in Google Sheets "Prompts" tab
- Easy to update without code changes

### Automation
- **GitHub Actions**: Automated daily execution (recommended)
- **PythonAnywhere**: Alternative hosting option

## 🛠️ Setup

### Prerequisites
- OpenAI API key
- Google Service Account with Sheets API access
- GitHub repository (for automation)

### Quick Start
1. Clone this repository
2. Set up Google Sheets credentials
3. Configure GitHub Secrets (see `GITHUB_ACTIONS_SETUP.md`)
4. Push to GitHub - automation starts immediately!

### Detailed Setup Guides
- [GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md) - Recommended approach
- [PythonAnywhere Setup](PYTHONANYWHERE_SETUP.md) - Alternative hosting
- [Configuration Guide](CONFIGURATION_README.md) - Google Sheets setup

## 📊 Output

### Google Sheets Structure
- **Daily Digest YYYY-MM-DD**: Raw article data for each day
- **Explainer Script**: 60-second daily briefings
- **One Sheet Briefing**: Comprehensive daily summaries
- **Keywords**: Configurable search terms by category
- **Prompts**: AI prompt templates

### Local Files
- CSV exports of daily results
- Log files for monitoring
- Text files of generated scripts

## 🔧 Configuration

### Keywords Management
Update search terms in the Google Sheets "Keywords" tab:
- Category: Group related keywords
- Keyword: Search term for Ground News
- Active: TRUE/FALSE to enable/disable

### Prompt Customization
Modify AI prompts in the "Prompts" tab:
- Explainer Script: 60-second briefing template
- One Sheet Briefing: Comprehensive summary template

## 🤖 Automation

### GitHub Actions (Recommended)
- Runs daily at 6:00 AM UTC
- Secure credential handling
- Automatic log collection
- Manual trigger available

### Schedule Customization
Edit `.github/workflows/daily-news-scraper.yml` to change timing:
```yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

## 📈 Monitoring

### Logs
- `ground_news_scraper.log` - Main scraper logs
- `explainer_script.log` - Script generation logs
- GitHub Actions artifacts for each run

### Outputs
- Check Google Sheets for new data
- Download artifacts from GitHub Actions
- Monitor OpenAI API usage

## 🔒 Security

- Credentials stored as GitHub Secrets
- No sensitive data in repository
- Service account with minimal permissions
- API key rotation recommended

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Run scraper
python ground_news_scraper.py
```

### Adding Features
1. Update keywords in Google Sheets
2. Modify prompts for different analysis
3. Extend scraper for additional sources
4. Customize output formats

## 📝 License

This project is for educational and research purposes. Please respect rate limits and terms of service for all APIs used.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes locally
4. Submit a pull request

## 📞 Support

- Check the setup guides for common issues
- Review GitHub Actions logs for debugging
- Verify Google Sheets permissions
- Monitor API usage and limits
