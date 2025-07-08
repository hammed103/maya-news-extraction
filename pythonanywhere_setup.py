#!/usr/bin/env python3

"""
PythonAnywhere Setup Script for Maya News Scraper

This script helps set up the daily news scraper on PythonAnywhere.
It creates the necessary task scheduler entry and sets up the environment.

Usage:
1. Upload all your files to PythonAnywhere
2. Set up your environment variables in a .env file
3. Run this script to configure the daily task
4. Manually add the task in PythonAnywhere's Tasks tab
"""

import os
import sys
from datetime import datetime

def create_env_template():
    """Create a template .env file for environment variables."""
    env_template = """# Environment variables for Maya News Scraper
# Copy this to .env and fill in your actual values

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Set timezone (default is UTC)
TZ=UTC
"""
    
    if not os.path.exists('.env'):
        with open('.env.template', 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template file")
        print("📝 Please copy this to .env and add your actual API keys")
    else:
        print("✅ .env file already exists")

def create_runner_script():
    """Create a runner script that loads environment variables."""
    runner_script = """#!/usr/bin/env python3

import os
import sys
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
def load_env():
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env()

# Configure logging for PythonAnywhere
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"maya_scraper_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

def main():
    try:
        # Import and run the main scraper
        from ground_news_scraper import main as scraper_main
        
        logging.info("Starting Maya News Scraper on PythonAnywhere")
        scraper_main()
        logging.info("Maya News Scraper completed successfully")
        
    except Exception as e:
        logging.error(f"Error running Maya News Scraper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open('run_daily_scraper.py', 'w') as f:
        f.write(runner_script)
    
    # Make it executable
    os.chmod('run_daily_scraper.py', 0o755)
    print("✅ Created run_daily_scraper.py")

def create_setup_instructions():
    """Create detailed setup instructions for PythonAnywhere."""
    instructions = """# PythonAnywhere Setup Instructions for Maya News Scraper

## Prerequisites
1. PythonAnywhere account (free or paid)
2. OpenAI API key
3. Google Service Account credentials (credentials.json)

## Setup Steps

### 1. Upload Files
Upload all your project files to your PythonAnywhere files directory:
- All Python scripts (.py files)
- requirements.txt
- credentials.json (Google Service Account)
- .env file (create from .env.template)

### 2. Install Dependencies
Open a Bash console in PythonAnywhere and run:
```bash
pip3.11 install --user -r requirements.txt
```

### 3. Set Up Environment Variables
1. Copy .env.template to .env
2. Edit .env and add your actual OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

### 4. Test the Setup
Run a test to make sure everything works:
```bash
python3.11 run_daily_scraper.py
```

### 5. Set Up Daily Task
1. Go to your PythonAnywhere Dashboard
2. Click on the "Tasks" tab
3. Click "Create a new scheduled task"
4. Set the following:
   - Command: `python3.11 /home/yourusername/run_daily_scraper.py`
   - Hour: 6 (or your preferred time)
   - Minute: 0
   - Description: "Maya Daily News Scraper"

### 6. Monitor Logs
Check the log files created in your directory:
- `maya_scraper_YYYYMMDD.log` - Daily scraper logs
- `ground_news_scraper.log` - Detailed scraper logs
- `explainer_script.log` - Explainer generation logs

## Troubleshooting

### Common Issues:
1. **Import errors**: Make sure all dependencies are installed with `--user` flag
2. **Permission errors**: Ensure credentials.json has proper permissions
3. **API errors**: Verify your OpenAI API key is correct and has credits
4. **Google Sheets errors**: Check that credentials.json is valid and has access

### File Paths:
Replace `/home/yourusername/` with your actual PythonAnywhere username path.

### Time Zone:
The default time is UTC. Adjust the scheduled task time according to your needs.

## Alternative: Manual Scheduling
If you prefer to run manually, you can:
1. Open a Bash console
2. Run: `python3.11 run_daily_scraper.py`
3. Set up a reminder to run this daily

## Monitoring
- Check the Tasks tab to see if your scheduled task is running
- Review log files for any errors
- Monitor your Google Sheets for new data
"""
    
    with open('PYTHONANYWHERE_SETUP.md', 'w') as f:
        f.write(instructions)
    print("✅ Created PYTHONANYWHERE_SETUP.md with detailed instructions")

def main():
    print("🚀 Setting up Maya News Scraper for PythonAnywhere")
    print("=" * 60)
    
    create_env_template()
    create_runner_script()
    create_setup_instructions()
    
    print("\n" + "=" * 60)
    print("✅ PythonAnywhere setup completed!")
    print("\nNext steps:")
    print("1. Copy .env.template to .env and add your API keys")
    print("2. Upload all files to PythonAnywhere")
    print("3. Follow instructions in PYTHONANYWHERE_SETUP.md")
    print("4. Set up the daily task in PythonAnywhere's Tasks tab")

if __name__ == "__main__":
    main()
