#!/usr/bin/env python3

"""
Test script to verify that the Google Sheets configuration system works properly.
This script tests both keyword and prompt loading from Google Sheets.
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def test_keywords_loading():
    """Test loading keywords from Google Sheets."""
    print("\n=== Testing Keywords Loading ===")
    
    try:
        # Import the function from ground_news_scraper
        from ground_news_scraper import load_keywords_from_sheet, get_fallback_categories
        
        print("Loading keywords from Google Sheets...")
        categories = load_keywords_from_sheet()
        
        if categories:
            print(f"✅ Successfully loaded {len(categories)} categories:")
            for category, keywords in categories.items():
                print(f"  - {category}: {len(keywords)} keywords")
                # Show first few keywords as sample
                sample_keywords = keywords[:3]
                if len(keywords) > 3:
                    sample_keywords.append("...")
                print(f"    Sample: {', '.join(sample_keywords)}")
            return True
        else:
            print("❌ Failed to load keywords from Google Sheets")
            return False
            
    except Exception as e:
        print(f"❌ Error testing keywords loading: {e}")
        return False


def test_prompts_loading():
    """Test loading prompts from Google Sheets."""
    print("\n=== Testing Prompts Loading ===")
    
    try:
        # Import the function from ground_news_scraper
        from ground_news_scraper import load_prompts_from_sheet, get_fallback_prompts
        
        print("Loading prompts from Google Sheets...")
        prompts = load_prompts_from_sheet()
        
        if prompts:
            print(f"✅ Successfully loaded {len(prompts)} prompts:")
            for prompt_name, prompt_text in prompts.items():
                print(f"  - {prompt_name}: {len(prompt_text)} characters")
                # Show first 100 characters as preview
                preview = prompt_text[:100].replace('\n', ' ')
                if len(prompt_text) > 100:
                    preview += "..."
                print(f"    Preview: {preview}")
            return True
        else:
            print("❌ Failed to load prompts from Google Sheets")
            return False
            
    except Exception as e:
        print(f"❌ Error testing prompts loading: {e}")
        return False


def test_nick_keywords_loading():
    """Test loading keywords from nick.py."""
    print("\n=== Testing Nick.py Keywords Loading ===")
    
    try:
        # Import the function from nick.py
        from nick import load_keywords_from_sheet, get_fallback_keywords
        
        print("Loading keywords from Google Sheets (nick.py)...")
        categories = load_keywords_from_sheet()
        
        if categories:
            print(f"✅ Successfully loaded {len(categories)} categories:")
            for category, keywords in categories.items():
                print(f"  - {category}: {len(keywords)} keywords")
            return True
        else:
            print("❌ Failed to load keywords from Google Sheets (nick.py)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing nick.py keywords loading: {e}")
        return False


def test_fallback_functionality():
    """Test that fallback functions work when Google Sheets is unavailable."""
    print("\n=== Testing Fallback Functionality ===")
    
    try:
        from ground_news_scraper import get_fallback_categories, get_fallback_prompts
        from nick import get_fallback_keywords
        
        # Test fallback categories
        fallback_categories = get_fallback_categories()
        print(f"✅ Fallback categories available: {len(fallback_categories)} categories")
        
        # Test fallback prompts
        fallback_prompts = get_fallback_prompts()
        print(f"✅ Fallback prompts available: {len(fallback_prompts)} prompts")
        
        # Test nick fallback keywords
        nick_fallback = get_fallback_keywords()
        print(f"✅ Nick fallback keywords available: {len(nick_fallback)} categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback functionality: {e}")
        return False


def test_credentials_file():
    """Test that credentials file exists."""
    print("\n=== Testing Credentials File ===")
    
    if os.path.exists("credentials.json"):
        print("✅ credentials.json file found")
        return True
    else:
        print("❌ credentials.json file not found")
        print("   Make sure you have the Google Sheets service account credentials file")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Google Sheets Configuration System")
    print("=" * 50)
    
    tests = [
        ("Credentials File", test_credentials_file),
        ("Keywords Loading", test_keywords_loading),
        ("Prompts Loading", test_prompts_loading),
        ("Nick Keywords Loading", test_nick_keywords_loading),
        ("Fallback Functionality", test_fallback_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Configuration system is working properly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
