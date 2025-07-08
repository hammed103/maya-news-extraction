import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import json
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("news_extraction.log"), logging.StreamHandler()],
)


# Google Sheets setup
def init_gspread():
    """Initialize Google Sheets client."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "/mnt/c/Users/hp/Desktop/Upwork/grounds/credentials.json", scope
    )
    client = gspread.authorize(creds)
    return client.open("Maya News Extraction").sheet1


def load_keywords_from_sheet():
    """Load keywords and categories from Google Sheets."""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "/mnt/c/Users/hp/Desktop/Upwork/grounds/credentials.json", scope
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open("Maya News Extraction")

        try:
            worksheet = spreadsheet.worksheet("Keywords")
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

            logging.info(f"Loaded {len(categories)} categories from Keywords sheet")
            return categories

        except gspread.WorksheetNotFound:
            logging.warning("Keywords sheet not found, using fallback categories")
            return get_fallback_keywords()

    except Exception as e:
        logging.error(f"Error loading keywords from sheet: {e}")
        return get_fallback_keywords()


def get_fallback_keywords():
    """Fallback keywords if Google Sheets is unavailable."""
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


# API headers
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://ground.news",
    "priority": "u=1, i",
    "referer": "https://ground.news/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
    "x-gn-v": "web",
}

# Keywords are now loaded from Google Sheets via load_keywords_from_sheet()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=20),
    retry=retry_if_exception_type(requests.exceptions.HTTPError),
    after=lambda retry_state: logging.info(
        f"Retrying request for '{retry_state.args[0]}' after {retry_state.next_action.sleep} seconds (attempt {retry_state.attempt_number})"
    ),
)
def fetch_articles(keyword):
    """Fetch articles from Ground.news API for a given keyword with retry logic."""
    try:
        json_data = {"url": keyword}
        response = requests.post(
            "https://web-api-cdn.ground.news/api/public/search/url",
            headers=headers,
            json=json_data,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()
        logging.info(f"API response for '{keyword}': {result}")
        if isinstance(result, dict) and "searchResults" in result:
            return result["searchResults"]
        elif isinstance(result, list):
            return result
        else:
            logging.warning(
                f"Unexpected response format for '{keyword}': {type(result)}"
            )
            return []
    except requests.HTTPError as e:
        logging.error(f"HTTP error fetching articles for keyword '{keyword}': {e}")
        raise
    except requests.RequestException as e:
        logging.error(f"Error fetching articles for keyword '{keyword}': {e}")
        return []


def parse_article(slug):
    """Parse article page using BeautifulSoup to extract details."""
    if not slug:
        logging.warning("No slug provided for article parsing")
        return None
    try:
        params = {"_rsc": "19oxi"}
        response = requests.get(
            f"https://ground.news/article/{slug}",
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Log a snippet of HTML for debugging
        logging.debug(f"HTML snippet for '{slug}': {str(soup)[:500]}...")

        # Extract headline
        headline_elem = (
            soup.find("h1")
            or soup.find(class_="headline")
            or soup.find(class_="article-title")
        )
        headline = headline_elem.get_text(strip=True) if headline_elem else "N/A"

        # Extract all sources
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
                or soup.find_all(
                    "a",
                    href=lambda x: x
                    and any(
                        domain in x.lower()
                        for domain in [
                            "cnn.com",
                            "reuters.com",
                            "nytimes.com",
                            "npr.org",
                            "foxnews.com",
                        ]
                    ),
                )
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
        source = ", ".join(sources) if sources else "N/A"
        if source != "N/A":
            logging.info(
                f"Sources extracted for '{slug}': {source} ({len(sources)} sources)"
            )
        else:
            # Log nearby elements and external links for debugging
            potential_source = (
                soup.find("div", class_=lambda x: x and "source" in x.lower())
                or soup.find("p", class_=lambda x: x and "source" in x.lower())
                or soup.find("span", class_=lambda x: x and "publisher" in x.lower())
                or soup.find(
                    "div",
                    class_="grid grid-cols-2 gap-y-[1rem] text-18 font-normal bg-tertiary-light dark:bg-dark-light p-[1rem]",
                )
            )
            external_links = soup.find_all(
                "a",
                href=lambda x: x
                and any(
                    domain in x.lower()
                    for domain in [
                        "cnn.com",
                        "reuters.com",
                        "nytimes.com",
                        "npr.org",
                        "foxnews.com",
                    ]
                ),
            )
            logging.warning(
                f"No sources found for '{slug}'. Tried primary <div> and classes: source, publication, article-source, publisher, source-attribution, byline, source-container, publisher-name, source-name, source-link, primary-source, article-meta. Nearby elements: {str(potential_source)[:200] if potential_source else 'None'}. External links: {[link.get('href') for link in external_links][:5]}"
            )

        # Extract summary (try <ul> first, then <span>, then fallback)
        summary_elem = soup.find(
            "ul", class_="list-outside list-disc pl-[8px] tablet:pl-[1rem]"
        )
        if summary_elem:
            summary_items = [
                li.get_text(strip=True) for li in summary_elem.find_all("li")
            ]
            summary = " ".join(summary_items) if summary_items else "N/A"
            logging.info(f"Summary extracted for '{slug}' using <ul> selector")
        else:
            summary_elem = soup.find(
                "span", class_="font-normal text-18 leading-9 break-words w-full"
            )
            if summary_elem:
                summary = (
                    summary_elem.get_text(strip=True)
                    if summary_elem.get_text(strip=True)
                    else "N/A"
                )
                logging.info(f"Summary extracted for '{slug}' using <span> selector")
            else:
                summary_elem = (
                    soup.find("div", class_="article-summary")
                    or soup.find("p", class_="description")
                    or soup.find("div", class_=lambda x: x and "summary" in x.lower())
                )
                summary = (
                    summary_elem.get_text(strip=True)
                    if summary_elem and summary_elem.get_text(strip=True)
                    else "N/A"
                )
                logging.info(f"Summary extracted for '{slug}' using fallback selector")

        if summary == "N/A":
            logging.warning(
                f"No summary found for '{slug}'. Tried classes: list-outside list-disc pl-[8px] tablet:pl-[1rem], font-normal text-18 leading-9 break-words w-full, article-summary, description, summary"
            )

        url = f"https://ground.news/article/{slug}"

        return {"headline": headline, "source": source, "url": url, "summary": summary}
    except (requests.RequestException, AttributeError) as e:
        logging.error(f"Error parsing article '{slug}': {e}")
        return None


def is_recent_article(article_date, days=30):
    """Check if article is within the last N days."""
    if not article_date:
        logging.info("No date provided, treating as recent")
        return True
    try:
        article_datetime = datetime.fromisoformat(article_date.replace("Z", "+00:00"))
        return article_datetime >= datetime.now().astimezone() - timedelta(days=days)
    except ValueError:
        logging.warning(f"Invalid date format: {article_date}, treating as non-recent")
        return False


def process_keyword(category, keyword, sheet):
    """Process a single keyword, fetch articles, and write to Google Sheet."""
    logging.info(f"Processing keyword: {keyword} (Category: {category})")
    articles = fetch_articles(keyword)
    skipped_articles = []

    if not isinstance(articles, list):
        logging.error(
            f"Expected a list of articles for '{keyword}', got: {type(articles)}"
        )
        return

    # Create skipped_articles folder if it doesn't exist
    os.makedirs("skipped_articles", exist_ok=True)

    for article in articles:
        if not isinstance(article, dict):
            logging.warning(
                f"Skipping invalid article format for '{keyword}': {article}"
            )
            skipped_articles.append(
                {"keyword": keyword, "article": article, "reason": "Invalid format"}
            )
            continue

        if article.get("type") != "event" or not is_recent_article(
            article.get("start", "")
        ):
            logging.info(
                f"Skipping article: {article.get('title', 'N/A')} (type: {article.get('type', 'N/A')}, date: {article.get('start', 'N/A')})"
            )
            skipped_articles.append(
                {
                    "keyword": keyword,
                    "title": article.get("title", "N/A"),
                    "type": article.get("type", "N/A"),
                    "date": article.get("start", "N/A"),
                    "reason": "Type or date filter",
                }
            )
            continue

        article_data = parse_article(article.get("slug"))
        if not article_data:
            skipped_articles.append(
                {
                    "keyword": keyword,
                    "title": article.get("title", "N/A"),
                    "reason": "Parsing failed",
                }
            )
            continue

        row = [
            article.get("start", "")[:10],
            category,
            keyword,
            article_data["headline"],
            article_data["source"],
            article_data["url"],
            article_data["summary"],
            datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%SZ"),
        ]

        existing_urls = [row[5] for row in sheet.get_all_values()[1:]]
        if article_data["url"] in existing_urls:
            logging.info(f"Skipping duplicate article: {article_data['url']}")
            skipped_articles.append(
                {
                    "keyword": keyword,
                    "title": article.get("title", "N/A"),
                    "reason": "Duplicate URL",
                }
            )
            continue

        try:
            sheet.append_row(row)
            logging.info(
                f"Successfully added article to sheet: {article_data['headline']}"
            )
        except gspread.exceptions.APIError as e:
            logging.error(f"Error writing to Google Sheet: {e}")
            skipped_articles.append(
                {
                    "keyword": keyword,
                    "title": article.get("title", "N/A"),
                    "reason": f"Sheet write error: {e}",
                }
            )
            continue

        time.sleep(5)  # Increased delay to avoid rate limits

    if skipped_articles:
        # Save to skipped_articles folder
        skipped_file = os.path.join(
            "skipped_articles", f"skipped_articles_{keyword}.json"
        )
        with open(skipped_file, "w") as f:
            json.dump(skipped_articles, f, indent=2)
        logging.info(
            f"Saved {len(skipped_articles)} skipped articles for '{keyword}' to {skipped_file}"
        )


def main():
    """Main function to process all keywords and write to Google Sheet."""
    sheet = init_gspread()

    # Load keywords from Google Sheets
    keywords_by_category = load_keywords_from_sheet()
    if not keywords_by_category:
        logging.error("Failed to load keywords. Exiting.")
        return

    if not sheet.get_all_values():
        header = [
            "Date",
            "Category",
            "Keyword",
            "Headline",
            "Source",
            "URL",
            "Summary",
            "Extraction Timestamp",
        ]
        sheet.append_row(header)
        logging.info("Added header to Google Sheet")

    for category, keywords in keywords_by_category.items():
        for keyword in keywords:
            process_keyword(category, keyword, sheet)
            time.sleep(5)  # Increased delay to avoid rate limits

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(sheet.get_all_values()[1:], columns=sheet.get_all_values()[0])
    df.to_csv(f"news_extraction_{timestamp}.csv", index=False)
    logging.info(f"Exported results to news_extraction_{timestamp}.csv")


if __name__ == "__main__":
    main()
