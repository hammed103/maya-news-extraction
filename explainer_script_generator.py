#!/usr/bin/env python3

import requests
import pandas as pd
import time
import pygsheets
import os
import logging
from datetime import datetime
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("explainer_script.log"), logging.StreamHandler()],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def init_google_sheet():
    """Initialize Google Sheets client and open the Maya News Extraction spreadsheet."""
    try:
        # Authorize with service account credentials
        client = pygsheets.authorize(service_file="credentials.json")
        # Open the spreadsheet by name
        sheet = client.open("Maya News Extraction")

        logging.info("Successfully connected to Google Sheet 'Maya News Extraction'")
        return sheet
    except Exception as e:
        logging.error(f"Error connecting to Google Sheet: {e}")
        return None


def get_daily_digest_data(sheet):
    """Get all data from today's Daily Digest sheet."""
    try:
        # Get today's sheet name
        today = datetime.now().strftime("%Y-%m-%d")
        sheet_name = f"Daily Digest {today}"

        # Try to get today's worksheet
        try:
            worksheet = sheet.worksheet_by_title(sheet_name)
            logging.info(f"Found '{sheet_name}' worksheet")
        except pygsheets.WorksheetNotFound:
            logging.error(f"'{sheet_name}' worksheet not found!")
            return None

        # Get all data from the sheet
        all_data = worksheet.get_all_values()

        if len(all_data) <= 1:  # Only header or empty
            logging.warning(f"No data found in '{sheet_name}' worksheet")
            return None

        # Convert to DataFrame for easier handling
        headers = all_data[0]
        data_rows = all_data[1:]
        df = pd.DataFrame(data_rows, columns=headers)

        logging.info(f"Retrieved {len(df)} articles from '{sheet_name}'")
        return df

    except Exception as e:
        logging.error(f"Error getting daily digest data: {e}")
        return None


def generate_explainer_script(summaries_data):
    """Generate a 60-second explainer script using OpenAI."""
    try:
        # Prepare the summaries for the prompt
        summaries_text = ""
        for idx, row in summaries_data.iterrows():
            category = row.get("Category", "Unknown")
            keyword = row.get("Keyword", "Unknown")
            headline = row.get("Headline", "Unknown")
            summary = row.get("Summary", "No summary available")

            summaries_text += f"\n{idx+1}. [{category} - {keyword}] {headline}\n   Summary: {summary}\n"

        prompt = f"""
        You are a U.S.-based political journalist creating a 60-second daily briefing for an audience deeply concerned with American democracy.

        Use the following spreadsheet of today's U.S. news stories to identify and summarize the items with the biggest impact on democracy—this includes developments related to voting rights, elections, disinformation, political extremism, civil liberties, court decisions, legislation, government transparency, and the rule of law.

        Your task: Write a concise, compelling 60-second script summarizing the top U.S. democracy-impacting news of the day.

        Tone: Clear, urgent, and accessible. Speak directly to a civically engaged but time-crunched audience.

        Format:
        - Start with a bold intro (e.g., "Today in American democracy…")
        - Prioritize 3–4 stories with the clearest implications for democratic institutions or civil rights
        - Use plain, powerful language—explain why each story matters
        - End with a short wrap-up or call to attention ("We'll be tracking this," etc.)

        Focus on U.S. stories first, but include significant international stories that impact global democracy if they're highly relevant.

        Spreadsheet input:
        {summaries_text}

        Write your 60-second democracy briefing (approximately 150-160 words):
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )

        script = response.choices[0].message.content.strip()
        logging.info("Successfully generated explainer script")
        return script

    except Exception as e:
        logging.error(f"Error generating explainer script: {e}")
        return None


def save_explainer_script(sheet, script, summaries_count):
    """Save the explainer script to the Explainer Script sheet."""
    try:
        sheet_name = "Explainer Script"

        # Try to get existing sheet or create new one
        try:
            worksheet = sheet.worksheet_by_title(sheet_name)
            logging.info(f"Found existing '{sheet_name}' worksheet")
            # Ensure the sheet has enough rows
            if worksheet.rows < 1000:
                worksheet.resize(rows=1000)
                logging.info("Expanded worksheet to 1000 rows")
        except pygsheets.WorksheetNotFound:
            worksheet = sheet.add_worksheet(sheet_name, rows=1000, cols=10)
            logging.info(f"Created new '{sheet_name}' worksheet")
            # Add headers for new sheet
            headers = ["Date", "Explainer"]
            worksheet.update_row(1, headers)

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if today's entry already exists
        all_data = worksheet.get_all_values()
        today_row = None
        for i, row in enumerate(all_data):
            if len(row) > 0 and row[0] == today:
                today_row = i + 1  # 1-based indexing
                break

        # Prepare the data to save
        data_row = [today, script]

        # Add or update today's entry
        if today_row:
            # Update existing entry
            worksheet.update_row(today_row, data_row)
            logging.info(f"Updated existing entry for {today}")
        else:
            # Add new entry using append_table which handles row positioning
            try:
                worksheet.append_table(data_row)
                logging.info(f"Added new entry for {today}")
            except Exception as e:
                # Fallback to manual row insertion
                next_row = len(all_data) + 1 if all_data else 2
                worksheet.update_row(next_row, data_row)
                logging.info(f"Added new entry for {today} at row {next_row}")

        logging.info(f"Successfully saved explainer script to '{sheet_name}'")
        return True

    except Exception as e:
        logging.error(f"Error saving explainer script: {e}")
        return False


def main():
    """Main function to generate and save explainer script."""
    logging.info("Starting explainer script generation...")

    # Initialize Google Sheets
    sheet = init_google_sheet()
    if not sheet:
        logging.error("Failed to initialize Google Sheet. Exiting.")
        return

    # Get today's daily digest data
    daily_data = get_daily_digest_data(sheet)
    if daily_data is None or daily_data.empty:
        logging.error("No daily digest data found. Exiting.")
        return

    logging.info(f"Processing {len(daily_data)} articles for explainer script")

    # Generate explainer script
    script = generate_explainer_script(daily_data)
    if not script:
        logging.error("Failed to generate explainer script. Exiting.")
        return

    # Save the script to Google Sheets
    success = save_explainer_script(sheet, script, len(daily_data))
    if success:
        logging.info("Explainer script generation completed successfully!")
        print("\n" + "=" * 60)
        print("GENERATED 60-SECOND EXPLAINER SCRIPT:")
        print("=" * 60)
        print(script)
        print("=" * 60)
    else:
        logging.error("Failed to save explainer script.")

    # Also save local copy
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"explainer_script_{today}.txt"
    with open(filename, "w") as f:
        f.write(f"Explainer Script for {today}\n")
        f.write(f"Based on {len(daily_data)} articles\n")
        f.write("=" * 60 + "\n\n")
        f.write(script)

    logging.info(f"Saved local copy to {filename}")


if __name__ == "__main__":
    main()
