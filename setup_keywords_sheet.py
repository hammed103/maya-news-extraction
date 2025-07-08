#!/usr/bin/env python3

import pygsheets


def setup_keywords_sheet():
    """Create and populate the Keywords sheet with current categories."""
    try:
        # Authorize with service account credentials
        client = pygsheets.authorize(service_file="credentials.json")
        # Open the spreadsheet by name
        sheet = client.open("Maya News Extraction")

        # Try to get existing Keywords sheet or create new one
        try:
            worksheet = sheet.worksheet_by_title("Keywords")
            print("Found existing 'Keywords' worksheet - will update")
            # Clear existing content
            worksheet.clear()
        except pygsheets.WorksheetNotFound:
            worksheet = sheet.add_worksheet("Keywords", rows=200, cols=10)
            print("Created new 'Keywords' worksheet")

        # Define current categories and keywords
        CATEGORIES = {
            "Press & Information Freedom": [
                "press freedom",
                "journalist arrested",
                "book ban",
                "curriculum ban",
                "library censorship",
                "disinformation",
                "media blackout",
                "anti-CRT",
                "newsroom raid",
            ],
            "Judicial & Legal Integrity": [
                "court independence",
                "due process",
                "habeas corpus",
                "rule of law",
                "judge removal",
                "legal overhaul",
                "military tribunal",
                "unconstitutional",
            ],
            "Voting Rights & Election Integrity": [
                "voter suppression",
                "gerrymandering",
                "election interference",
                "ballot access",
                "poll closures",
                "voter ID laws",
                "disinformation campaign",
                "electoral fraud claims",
            ],
            "Checks, Balances & Rule of Law": [
                "executive overreach",
                "constitutional crisis",
                "legislative bypass",
                "SCOTUS ignored",
                "emergency powers",
                "separation of powers",
            ],
            "Institutional Capture": [
                "DOJ politicization",
                "education department purge",
                "NSC shake-up",
                "civil service loyalty oath",
                "deep state",
                "Trump loyalists installed",
            ],
            "Civic Resistance & Whistleblowing": [
                "protest crackdown",
                "whistleblower",
                "civil disobedience",
                "lawsuit filed",
                "watchdog report",
                "leaked memo",
                "activist arrested",
            ],
            "Economic Power & Authoritarianism": [
                "union busting",
                "labor strike suppressed",
                "corporate lobbying",
                "anti-worker law",
                "economic coercion",
                "monopoly power",
            ],
            "Immigration, Policing & Detention": [
                "mass detention",
                "ICE raid",
                "border wall",
                "family separation",
                "surveillance program",
                "immigrant abuse",
                "asylum denied",
            ],
            "Surveillance & Tech Manipulation": [
                "facial recognition",
                "app ban",
                "AI censorship",
                "algorithmic bias",
                "digital surveillance",
                "metadata collection",
                "social media manipulation",
            ],
            "Cultural Control & Civil Rights Erosion": [
                "anti-LGBTQ+ law",
                "drag ban",
                "bathroom bill",
                "book removal",
                "censorship law",
                "identity policing",
                "anti-DEI",
                "religious exemption law",
            ],
            "Global Authoritarian Networks": [
                "Orbán",
                "Netanyahu",
                "Modi",
                "Erdogan",
                "global authoritarianism",
                "democracy backsliding",
                "transnational repression",
                "illiberal democracy",
            ],
        }

        # Convert to list format for Google Sheets
        categories_data = [["Category", "Keyword", "Active"]]

        for category, keywords in CATEGORIES.items():
            for keyword in keywords:
                categories_data.append([category, keyword, "TRUE"])

        # Add all data to the sheet
        for i, row in enumerate(categories_data):
            worksheet.update_row(i + 1, row)

        keyword_count = len(categories_data) - 1
        print(f"Keywords sheet populated with {keyword_count} entries")
        print("\nInstructions for use:")
        print("- Column A: Category name")
        print("- Column B: Keyword to search for")
        print("- Column C: Active (TRUE/FALSE) - set to FALSE to disable")
        print("\nYou can now easily modify keywords directly in Google Sheet!")

    except Exception as e:
        print(f"Error setting up Keywords sheet: {e}")


if __name__ == "__main__":
    setup_keywords_sheet()
