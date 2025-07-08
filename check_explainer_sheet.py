#!/usr/bin/env python3

import pygsheets
import os
from datetime import datetime

def check_explainer_sheet():
    """Check what's in the Explainer Script sheet."""
    try:
        # Authorize with service account credentials
        client = pygsheets.authorize(service_file="credentials.json")
        # Open the spreadsheet by name
        sheet = client.open("Maya News Extraction")
        
        # Get the Explainer Script worksheet
        try:
            worksheet = sheet.worksheet_by_title("Explainer Script")
            print(f"Found 'Explainer Script' worksheet")
            
            # Get all data
            all_data = worksheet.get_all_values()
            print(f"Total rows in sheet: {len(all_data)}")
            
            # Show first few rows
            print("\nFirst 10 rows:")
            for i, row in enumerate(all_data[:10]):
                print(f"Row {i+1}: {row}")
            
            # Check for today's date
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"\nLooking for today's date: {today}")
            
            found_today = False
            for i, row in enumerate(all_data):
                if len(row) > 0 and row[0] == today:
                    print(f"Found today's entry at row {i+1}: {row[0]}")
                    if len(row) > 1:
                        print(f"Script preview: {row[1][:100]}...")
                    found_today = True
                    break
            
            if not found_today:
                print("No entry found for today's date")
                
        except Exception as e:
            print(f"Error accessing Explainer Script sheet: {e}")
            
    except Exception as e:
        print(f"Error connecting to Google Sheet: {e}")

if __name__ == "__main__":
    check_explainer_sheet()
