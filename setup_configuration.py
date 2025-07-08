#!/usr/bin/env python3

"""
Comprehensive setup script to initialize both Keywords and Prompts sheets
in Google Sheets for the Maya News Extraction system.
"""

import sys
import logging
from setup_keywords_sheet import setup_keywords_sheet
from setup_prompts_sheet import setup_prompts_sheet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main():
    """Run both setup scripts to initialize the configuration system."""
    print("🚀 Setting up Maya News Extraction Configuration System")
    print("=" * 60)
    
    success_count = 0
    total_setups = 2
    
    # Setup Keywords sheet
    print("\n📋 Setting up Keywords sheet...")
    try:
        setup_keywords_sheet()
        print("✅ Keywords sheet setup completed successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Keywords sheet setup failed: {e}")
        logging.error(f"Keywords sheet setup error: {e}")
    
    # Setup Prompts sheet
    print("\n💬 Setting up Prompts sheet...")
    try:
        setup_prompts_sheet()
        print("✅ Prompts sheet setup completed successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Prompts sheet setup failed: {e}")
        logging.error(f"Prompts sheet setup error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Setup Summary:")
    print(f"  ✅ Successful setups: {success_count}/{total_setups}")
    
    if success_count == total_setups:
        print("\n🎉 Configuration system setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Run 'python test_configuration.py' to verify the setup")
        print("2. Update keywords and prompts directly in Google Sheets as needed")
        print("3. Your scrapers will now read from Google Sheets automatically")
        print("\n💡 Tips:")
        print("- Set 'Active' to FALSE to disable specific keywords or prompts")
        print("- Add new keywords by adding rows to the Keywords sheet")
        print("- Modify prompts by editing the 'Prompt Text' column")
        return 0
    else:
        print("\n⚠️  Some setups failed. Please check the errors above.")
        print("Make sure you have:")
        print("- Valid credentials.json file")
        print("- Proper Google Sheets API access")
        print("- 'Maya News Extraction' spreadsheet exists")
        return 1

if __name__ == "__main__":
    sys.exit(main())
