#!/usr/bin/env python3

import pygsheets


def setup_prompts_sheet():
    """Create and populate the Prompts sheet with OpenAI prompts."""
    try:
        # Authorize with service account credentials
        client = pygsheets.authorize(service_file="credentials.json")
        # Open the spreadsheet by name
        sheet = client.open("Maya News Extraction")
        
        # Try to get existing Prompts sheet or create new one
        try:
            worksheet = sheet.worksheet_by_title("Prompts")
            print("Found existing 'Prompts' worksheet - will update")
            # Clear existing content
            worksheet.clear()
        except pygsheets.WorksheetNotFound:
            worksheet = sheet.add_worksheet("Prompts", rows=50, cols=10)
            print("Created new 'Prompts' worksheet")
        
        # Define the prompts used in the system
        prompts_data = [
            ["Prompt Name", "Prompt Text", "Active"],
            [
                "Explainer Script",
                """You are a U.S.-based political journalist creating a 60-second daily briefing for an audience deeply concerned with American democracy.

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

Write your 60-second democracy briefing (approximately 150-160 words):""",
                "TRUE"
            ],
            [
                "One Sheet Briefing",
                """Acting as a news producer for a political update show, please use the spreadsheet to create a one-sheet of the news that is most critical to preserving US democracy.

Your task: Create a comprehensive one-sheet briefing document that covers the most critical democracy-related news from today's stories.

Format:
- Start with a brief executive summary paragraph
- Organize stories into thematic sections (e.g., "Voting Rights", "Court Decisions", "Legislative Actions", "Civil Liberties")
- For each story, provide: headline, key details, and why it matters for democracy
- Include a "What to Watch" section highlighting ongoing developments
- End with key takeaways for democracy advocates

Focus on stories that have the most significant impact on democratic institutions, civil rights, voting access, government transparency, and the rule of law.

Spreadsheet input:
{summaries_text}

Create your comprehensive one-sheet briefing:""",
                "TRUE"
            ],
            [
                "US Article Filter",
                """Determine if this news article is about United States domestic news or politics.

Article details:
Headline: {headline}
Summary: {summary}
Source: {source}

Instructions:
- Return "YES" if this article is primarily about US domestic news, politics, government, elections, civil rights, or other US-specific issues
- Return "NO" if this article is about international news, foreign countries, or global issues that don't directly impact US domestic affairs
- Focus on whether the story has direct relevance to American democracy, US politics, or US domestic policy

Examples:
- US Supreme Court ruling → YES
- California governor election → YES
- UK Parliament vote → NO
- International trade deal → NO (unless it specifically impacts US domestic policy)
- US military action abroad → NO (unless it impacts domestic politics)

Response (just YES or NO):""",
                "TRUE"
            ]
        ]
        
        # Add all data to the sheet
        for i, row in enumerate(prompts_data):
            worksheet.update_row(i + 1, row)
        
        prompt_count = len(prompts_data) - 1
        print(f"Prompts sheet populated with {prompt_count} prompts")
        print("\nInstructions for use:")
        print("- Column A: Prompt name/identifier")
        print("- Column B: Full prompt text")
        print("- Column C: Active (TRUE/FALSE) - set to FALSE to disable")
        print("\nYou can now modify prompts directly in Google Sheet!")
        
    except Exception as e:
        print(f"Error setting up Prompts sheet: {e}")


if __name__ == "__main__":
    setup_prompts_sheet()
