import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import pandas as pd
import time
import pygsheets
import os
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ground_news_scraper.log"), logging.StreamHandler()],
)

HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://ground.news",
    "referer": "https://ground.news/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "x-gn-v": "web",
}

# Initialize OpenAI client
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and openai_api_key.strip():
        # Debug: Check OpenAI version and API key format
        import openai

        logging.info(f"OpenAI library version: {openai.__version__}")
        logging.info(f"API key format check: {openai_api_key.strip()[:10]}...")

        # Initialize client according to v1+ documentation
        openai_client = OpenAI(api_key=openai_api_key.strip())

        # Test the client with a simple call
        logging.info("Testing OpenAI client connection...")
        test_response = openai_client.models.list()
        logging.info("OpenAI client initialized and tested successfully")
    else:
        openai_client = None
        logging.warning("OPENAI_API_KEY not found - AI features will be disabled")
except Exception as e:
    openai_client = None
    logging.error(f"Failed to initialize OpenAI client: {e}")
    logging.error(f"Exception type: {type(e).__name__}")
    logging.error("AI features will be disabled")

# Cache for configuration data to avoid repeated API calls
_cached_keywords = None
_cached_prompts = None
_cache_timestamp = None
CACHE_DURATION = 300  # 5 minutes in seconds


def get_google_client():
    """Get authenticated Google Sheets client."""
    google_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if google_creds:
        import json
        import tempfile

        # Create temporary credentials file from environment variable
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_file.write(google_creds)
            temp_creds_path = temp_file.name
        client = pygsheets.authorize(service_file=temp_creds_path)
        # Clean up temp file
        os.unlink(temp_creds_path)
        return client
    else:
        # Fall back to local credentials file
        return pygsheets.authorize(service_file="credentials.json")


def load_keywords_from_sheet():
    """Load keywords and categories from Google Sheets with caching."""
    global _cached_keywords, _cache_timestamp

    # Check if cache is still valid
    current_time = time.time()
    if (
        _cached_keywords is not None
        and _cache_timestamp is not None
        and current_time - _cache_timestamp < CACHE_DURATION
    ):
        logging.debug("Using cached keywords")
        return _cached_keywords

    try:
        client = get_google_client()
        sheet = client.open("Maya News Extraction")

        try:
            worksheet = sheet.worksheet_by_title("Keywords")
            # Get all data from the Keywords sheet
            data = worksheet.get_all_records()

            # Build categories dictionary from sheet data
            categories = {}
            for row in data:
                if row.get("Active", "").upper() == "TRUE":
                    category = row.get("Category", "")
                    keyword = row.get("Keyword", "")
                    if category and keyword:
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(keyword)

            # Cache the results
            _cached_keywords = categories
            _cache_timestamp = current_time

            logging.info(f"Loaded {len(categories)} categories from Keywords sheet")
            return categories

        except pygsheets.WorksheetNotFound:
            logging.warning("Keywords sheet not found, using fallback categories")
            fallback = get_fallback_categories()
            _cached_keywords = fallback
            _cache_timestamp = current_time
            return fallback

    except Exception as e:
        logging.error(f"Error loading keywords from sheet: {e}")
        fallback = get_fallback_categories()
        _cached_keywords = fallback
        _cache_timestamp = current_time
        return fallback


def load_prompts_from_sheet():
    """Load OpenAI prompts from Google Sheets."""
    try:
        client = get_google_client()
        sheet = client.open("Maya News Extraction")

        try:
            worksheet = sheet.worksheet_by_title("Prompts")
            # Get all data from the Prompts sheet
            data = worksheet.get_all_records()

            # Build prompts dictionary from sheet data
            prompts = {}
            for row in data:
                if row.get("Active", "").upper() == "TRUE":
                    prompt_name = row.get("Prompt Name", "")
                    prompt_text = row.get("Prompt Text", "")
                    if prompt_name and prompt_text:
                        prompts[prompt_name] = prompt_text

            logging.info(f"Loaded {len(prompts)} prompts from Prompts sheet")
            return prompts

        except pygsheets.WorksheetNotFound:
            logging.warning("Prompts sheet not found, using fallback prompts")
            return get_fallback_prompts()

    except Exception as e:
        logging.error(f"Error loading prompts from sheet: {e}")
        return get_fallback_prompts()


def get_fallback_categories():
    """Fallback categories if Google Sheets is unavailable."""
    return {
        "Press & Information Freedom": [
            "press freedom",
            "journalist arrested",
            "book ban",
            "disinformation",
        ],
        "Voting Rights & Election Integrity": [
            "voter suppression",
            "gerrymandering",
            "election interference",
        ],
        "Judicial & Legal Integrity": [
            "court independence",
            "due process",
            "rule of law",
        ],
    }


def get_fallback_prompts():
    """Fallback prompts if Google Sheets is unavailable."""
    return {
        "Explainer Script": (
            "You are a U.S.-based political journalist creating a 60-second "
            "daily briefing for an audience deeply concerned with American "
            "democracy. Write a concise, compelling script summarizing the "
            "top U.S. democracy-impacting news of the day. Start with "
            "'Today in American democracy...' and prioritize 3-4 stories. "
            "Spreadsheet input: {summaries_text}"
        ),
        "One Sheet Briefing": (
            "Create a comprehensive one-sheet briefing document covering "
            "the most critical democracy-related news. Organize into "
            "thematic sections and focus on democratic institutions impact. "
            "Spreadsheet input: {summaries_text}"
        ),
        "US Article Filter": (
            "Determine if this news article is about United States domestic "
            "news or politics. Return 'YES' for US domestic news, 'NO' for "
            "international. Article: Headline: {headline}, "
            "Summary: {summary}, Source: {source}"
        ),
    }


def init_google_sheet():
    """Initialize Google Sheets client and open the Maya News Extraction spreadsheet."""
    try:
        # Authorize with service account credentials
        client = get_google_client()
        # Open the spreadsheet by name
        sheet = client.open("Maya News Extraction")

        # Create daily sheet name with current date
        today = datetime.now().strftime("%Y-%m-%d")
        sheet_name = f"Daily Digest {today}"

        # Try to get today's worksheet, create if it doesn't exist
        try:
            worksheet = sheet.worksheet_by_title(sheet_name)
            logging.info(f"Found existing '{sheet_name}' worksheet")
        except pygsheets.WorksheetNotFound:
            worksheet = sheet.add_worksheet(sheet_name)
            logging.info(f"Created new '{sheet_name}' worksheet")

        logging.info("Successfully connected to Google Sheet 'Maya News Extraction'")
        return worksheet
    except Exception as e:
        logging.error(f"Error connecting to Google Sheet: {e}")
        return None


def post_with_retry(url, headers, json_data, retries=3, delay=3):
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=json_data, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt+1} failed for '{json_data['url']}': {e}")
            time.sleep(delay)
    return None


def generate_explainer_script(daily_data):
    """Generate a 60-second explainer script using OpenAI."""
    try:
        # Check if OpenAI client is available
        if openai_client is None:
            logging.warning(
                "OpenAI client not available, skipping explainer script generation"
            )
            return None

        # Load prompts from Google Sheets
        prompts = load_prompts_from_sheet()

        # Prepare the summaries for the prompt
        summaries_text = ""
        for idx, row in daily_data.iterrows():
            category = row.get("Category", "Unknown")
            keyword = row.get("Keyword", "Unknown")
            headline = row.get("Headline", "Unknown")
            summary = row.get("Summary", "No summary available")

            summaries_text += f"\n{idx+1}. [{category} - {keyword}] {headline}\n   Summary: {summary}\n"

        # Get the explainer script prompt from Google Sheets
        prompt_template = prompts.get(
            "Explainer Script", get_fallback_prompts()["Explainer Script"]
        )
        prompt = prompt_template.format(summaries_text=summaries_text)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5,
        )

        script = response.choices[0].message.content.strip()
        # Clean up any markdown formatting
        script = script.replace("**", "").replace("##", "").replace("###", "")
        script = script.replace("# ", "").strip()
        logging.info("Successfully generated explainer script")
        return script

    except Exception as e:
        logging.error(f"Error generating explainer script: {e}")
        return None


def generate_one_sheet(daily_data):
    """Generate a longer one-sheet news summary using OpenAI."""
    try:
        # Check if OpenAI client is available
        if openai_client is None:
            logging.warning(
                "OpenAI client not available, skipping one-sheet generation"
            )
            return None

        # Load prompts from Google Sheets
        prompts = load_prompts_from_sheet()

        # Prepare the summaries for the prompt
        summaries_text = ""
        for idx, row in daily_data.iterrows():
            category = row.get("Category", "Unknown")
            keyword = row.get("Keyword", "Unknown")
            headline = row.get("Headline", "Unknown")
            summary = row.get("Summary", "No summary available")

            summaries_text += f"\n{idx+1}. [{category} - {keyword}] {headline}\n   Summary: {summary}\n"

        # Get the one-sheet briefing prompt from Google Sheets
        prompt_template = prompts.get(
            "One Sheet Briefing", get_fallback_prompts()["One Sheet Briefing"]
        )
        prompt = prompt_template.format(summaries_text=summaries_text)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5,
        )

        one_sheet = response.choices[0].message.content.strip()
        # Clean up any markdown formatting
        one_sheet = one_sheet.replace("**", "").replace("##", "").replace("###", "")
        one_sheet = one_sheet.replace("# ", "").strip()
        logging.info("Successfully generated one-sheet briefing")
        return one_sheet

    except Exception as e:
        logging.error(f"Error generating one-sheet briefing: {e}")
        return None


def save_explainer_script(sheet, script):
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
            logging.info(f"Updated existing explainer script for {today}")
        else:
            # Add new entry using append_table which handles row positioning
            try:
                worksheet.append_table(data_row)
                logging.info(f"Added new explainer script for {today}")
            except Exception:
                # Fallback to manual row insertion
                next_row = len(all_data) + 1 if all_data else 2
                worksheet.update_row(next_row, data_row)
                logging.info(
                    f"Added new explainer script for {today} at row {next_row}"
                )

        logging.info(f"Successfully saved explainer script to '{sheet_name}'")
        return True

    except Exception as e:
        logging.error(f"Error saving explainer script: {e}")
        return False


def save_one_sheet(sheet, one_sheet):
    """Save the one-sheet briefing to the One Sheet sheet."""
    try:
        sheet_name = "One Sheet"

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
            headers = ["Date", "One Sheet Briefing"]
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
        data_row = [today, one_sheet]

        # Add or update today's entry
        if today_row:
            # Update existing entry
            worksheet.update_row(today_row, data_row)
            logging.info(f"Updated existing one-sheet for {today}")
        else:
            # Add new entry using append_table which handles row positioning
            try:
                worksheet.append_table(data_row)
                logging.info(f"Added new one-sheet for {today}")
            except Exception:
                # Fallback to manual row insertion
                next_row = len(all_data) + 1 if all_data else 2
                worksheet.update_row(next_row, data_row)
                logging.info(f"Added new one-sheet for {today} at row {next_row}")

        logging.info(f"Successfully saved one-sheet to '{sheet_name}'")
        return True

    except Exception as e:
        logging.error(f"Error saving one-sheet: {e}")
        return False


def is_us_based_article(headline, summary, source):
    """Use OpenAI to determine if article is US-based news."""
    try:
        # Check if OpenAI client is available
        if openai_client is None:
            logging.warning("OpenAI client not available, including all articles")
            return True

        # Load prompts from Google Sheets
        prompts = load_prompts_from_sheet()

        # Get the US article filter prompt from Google Sheets
        prompt_template = prompts.get(
            "US Article Filter", get_fallback_prompts()["US Article Filter"]
        )
        prompt = prompt_template.format(
            headline=headline, summary=summary, source=source
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.1,
        )

        result = response.choices[0].message.content.strip().upper()
        # Clean up any markdown formatting
        result = result.replace("**", "").replace("##", "").replace("#", "").strip()

        if result == "YES":
            return True
        elif result == "NO":
            return False
        else:
            # If unclear response, default to including the article
            logging.warning(f"Unclear OpenAI response for US filtering: '{result}'")
            return True

    except Exception as e:
        logging.error(f"Error with OpenAI US filtering: {e}")
        # If OpenAI fails, default to including the article
        return True


def extract_summary(slug):
    try:
        article_url = f"https://ground.news/article/{slug}"
        params = {"_rsc": "19oxi"}
        r = requests.get(article_url, params=params, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract headline
        headline_elem = (
            soup.find("h1")
            or soup.find(class_="headline")
            or soup.find(class_="article-title")
        )
        headline = headline_elem.get_text(strip=True) if headline_elem else ""

        # Extract all sources using comprehensive method from nick.py
        source_divs = soup.find_all(
            "div",
            class_="flex font-bold bg-light-light dark:bg-tertiary-light dark:text-dark-primary rounded-full px-[0.6rem] py-[5px] gap-[8px] items-center shrink-0",
        )
        sources = []
        for div in source_divs:
            source_span = div.find("span")
            if source_span:
                source_text = source_span.get_text(strip=True)
                if source_text:
                    sources.append(source_text)

        # Fallback: Try other source containers or links
        if not sources:
            source_elems = (
                soup.find_all(class_="source")
                or soup.find_all(class_="publication")
                or soup.find_all(class_="article-source")
                or soup.find_all(class_="publisher")
                or soup.find_all(class_="source-attribution")
                or soup.find_all(class_="byline")
                or soup.find_all(class_="source-container")
                or soup.find_all(class_="publisher-name")
                or soup.find_all(class_="source-name")
                or soup.find_all(class_="source-link")
                or soup.find_all(class_="primary-source")
                or soup.find_all(class_="article-meta")
                or soup.find_all("span", class_=lambda x: x and "source" in x.lower())
                or soup.find_all("div", class_=lambda x: x and "publisher" in x.lower())
                or soup.find_all("span", class_=lambda x: x and "byline" in x.lower())
            )
            for elem in source_elems:
                source_text = elem.get_text(strip=True)
                if source_text and source_text not in sources:
                    sources.append(source_text)

        # Text-based search for sources if none found
        if not sources:
            for elem in soup.find_all(["span", "div", "p"]):
                text = elem.get_text(strip=True).lower()
                if "published by" in text or "source:" in text:
                    source_text = elem.get_text(strip=True)
                    if source_text and source_text not in sources:
                        sources.append(source_text)

        # Combine sources into a comma-separated string
        source = ", ".join(sources) if sources else ""

        # Extract summary
        summary = soup.find("meta", {"name": "description"})
        summary = summary["content"] if summary else ""

        return headline, summary, article_url, source
    except Exception as e:
        logging.error(f"Error scraping article: {e}")
        return "", "", "", ""


# Categories are now loaded from Google Sheets via load_keywords_from_sheet()


def main():
    # Initialize Google Sheet
    worksheet = init_google_sheet()
    if not worksheet:
        logging.error("Failed to initialize Google Sheet. Exiting.")
        return

    # Load keywords from Google Sheets
    categories = load_keywords_from_sheet()
    if not categories:
        logging.error("Failed to load keywords. Exiting.")
        return

    # Define the expected header
    expected_header = [
        "Date",
        "Category",
        "Keyword",
        "Headline",
        "Source",
        "URL",
        "Summary",
        "Extraction Timestamp",
    ]

    # Check if sheet has correct headers
    existing_data = worksheet.get_all_values()
    if not existing_data or existing_data[0] != expected_header:
        # Clear the sheet and add correct headers
        worksheet.clear()
        worksheet.update_row(1, expected_header)
        logging.info("Added/Updated header to Google Sheet")
        existing_data = [expected_header]  # Update existing_data to reflect new state
    else:
        # Get fresh data if headers were already correct
        existing_data = worksheet.get_all_values()

    # Get existing URLs to avoid duplicates
    existing_urls = (
        [row[5] for row in existing_data[1:]] if len(existing_data) > 1 else []
    )

    results = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=2)

    for category, keywords in categories.items():
        for keyword in keywords:
            logging.info(f"Searching: {keyword} in category {category}")
            response = post_with_retry(
                "https://web-api-cdn.ground.news/api/public/search/url",
                HEADERS,
                {"url": keyword},
            )
            if not response:
                continue
            try:
                json_data = response.json()
                for item in json_data.get("searchResults", []):
                    if item.get("type") == "event":
                        date_str = item.get("start", "")
                        date = (
                            datetime.fromisoformat(date_str.replace("Z", "")).replace(
                                tzinfo=timezone.utc
                            )
                            if date_str
                            else None
                        )
                        if not date or date < cutoff_date:
                            continue
                        slug = item.get("slug", "")
                        headline, summary, article_url, source = extract_summary(slug)

                        # Skip if URL already exists
                        if article_url in existing_urls:
                            logging.info(f"Skipping duplicate article: {article_url}")
                            continue

                        # Filter for US-based articles only
                        if not is_us_based_article(headline, summary, source):
                            logging.info(f"Skipping non-US article: {headline}")
                            continue

                        row_data = [
                            date.date().isoformat(),
                            category,
                            keyword,
                            headline,
                            source,
                            article_url,
                            summary,
                            datetime.now(timezone.utc).isoformat(),
                        ]

                        # Add to Google Sheet
                        try:
                            # Find the next empty row
                            next_row = len(existing_data) + 1
                            worksheet.update_row(next_row, row_data)
                            logging.info(f"Added article to Google Sheet: {headline}")
                            existing_urls.append(article_url)
                            # Update existing_data to reflect the new row
                            existing_data.append(row_data)
                        except Exception as e:
                            logging.error(f"Error adding to Google Sheet: {e}")

                        # Also keep in local results
                        results.append(
                            {
                                "Date": date.date(),
                                "Category": category,
                                "Keyword": keyword,
                                "Headline": headline,
                                "Source": source,
                                "URL": article_url,
                                "Summary": summary,
                                "Extraction Timestamp": datetime.now(
                                    timezone.utc
                                ).isoformat(),
                            }
                        )

                        # Avoid rate limiting
                        time.sleep(2)
            except Exception as e:
                logging.error(f"Error processing {keyword}: {e}")

    # Save local copy as CSV
    df = pd.DataFrame(results)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"ground_news_results_{timestamp}.csv"
    df.to_csv(filename, index=False)
    logging.info(f"Done. {len(df)} articles saved to {filename} and Google Sheet")

    # Generate both explainer script and one-sheet if we have articles
    if len(df) > 0:
        logging.info("Generating explainer script and one-sheet...")

        # Generate 60-second explainer script
        script = generate_explainer_script(df)

        # Generate one-sheet briefing
        one_sheet = generate_one_sheet(df)

        if script or one_sheet:
            # Get the main spreadsheet object for saving
            try:
                client = get_google_client()
                sheet = client.open("Maya News Extraction")

                # Save 60-second explainer script
                if script:
                    success = save_explainer_script(sheet, script)
                    if success:
                        logging.info("60-second explainer script generated and saved!")
                        print("\n" + "=" * 60)
                        print("GENERATED 60-SECOND EXPLAINER SCRIPT:")
                        print("=" * 60)
                        print(script)
                        print("=" * 60)
                    else:
                        logging.error("Failed to save explainer script")

                # Save one-sheet briefing
                if one_sheet:
                    success = save_one_sheet(sheet, one_sheet)
                    if success:
                        logging.info("One-sheet briefing generated and saved!")
                        print("\n" + "=" * 60)
                        print("GENERATED ONE-SHEET BRIEFING:")
                        print("=" * 60)
                        print(one_sheet)
                        print("=" * 60)
                    else:
                        logging.error("Failed to save one-sheet briefing")

            except Exception as e:
                logging.error(f"Error saving outputs: {e}")
        else:
            logging.error("Failed to generate both outputs")
    else:
        logging.info("No articles found, skipping output generation")


if __name__ == "__main__":
    main()
