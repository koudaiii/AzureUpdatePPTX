import sys
import os
import requests
import logging
import re
import feedparser
import urllib.parse as urlparse
from datetime import datetime, timedelta
from openai import AzureOpenAI
from bs4 import BeautifulSoup

# How many days back to include updates in slides
DAYS = 7

# Azure Updates API URL
BASE_URL = "https://www.microsoft.com/releasecommunications/api/v2/azure/"


# Generate RSS feed URL from URL
def rss_url(url):
    return f"{url}rss"


# System prompt configuration (default is Japanese, actually specified when called)
systemprompt = ("渡されたデータに含まれている Azure のアップデート情報を日本語で 3 行程度で要約してください。" +
                "各提供する地域のリージョンについては、翻訳せずに英語表記のままにしてください。" +
                "リンク用のURLやマークダウンは含まず、プレーンテキストで出力してください。")


# Date format 'Thu, 23 Jan 2025 21:30:21 Z' is used in RSS feed published field
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %z'

# Timezone specification
os.environ['TZ'] = 'UTC'


# Environment variable check
def environment_check():
    if (os.getenv("API_KEY") == "" or os.getenv("API_KEY") is None or
            os.getenv("API_ENDPOINT") == "") or os.getenv("API_ENDPOINT") is None:
        logging.error('Environment variables are missing. Please check the .env file. (環境変数が不足しています。.env ファイルを確認してください。)')
        return False
    else:
        return True


# Function to generate Azure OpenAI client
def azure_openai_client(key, endpoint):
    parsed_url = urlparse.urlparse(endpoint)
    query_params = dict(urlparse.parse_qsl(parsed_url.query))
    if query_params is None:
        logging.error("Query Parameters are not found in the endpoint URL.")
        return None, None

    api_version = query_params.get('api-version', '')
    if api_version == '' or api_version is None:
        logging.error("API Version is not found in the endpoint URL.")
        return None, None

    deployment_name_match = re.search(r"deployments/([^/]+)/", parsed_url.path)
    deployment_name = deployment_name_match.group(1) if deployment_name_match else ''
    if deployment_name == '':
        logging.error("Deployment Name is not found in the endpoint URL.")
        return None, None

    logging.debug(f"Extracted API Key: {key}")
    logging.debug(f"Extracted API Version: {api_version}")
    logging.debug(f"Extracted Deployment Name: {deployment_name}")

    return AzureOpenAI(api_key=key, api_version=api_version, azure_endpoint=endpoint), deployment_name


# Get latest article date from entries
def latest_article_date(entries):
    if len(entries) == 0:
        return None
    # Convert to date format yyyy-mm-dd
    return datetime.strptime(entries[0].published, DATE_FORMAT).astimezone().strftime('%Y-%m-%d')


# Get oldest article date from entries
def oldest_article_date(entries):
    if len(entries) == 0:
        return None
    # Convert to date format yyyy-mm-dd
    return datetime.strptime(entries[-1].published, DATE_FORMAT).astimezone().strftime('%Y-%m-%d')


# Read Azure Updates RSS feed and get entries
def get_rss_feed_entries():
    feed = feedparser.parse(rss_url(BASE_URL))
    return feed.entries


# List URLs of entries within specified days from entries
def get_update_urls(days):
    entries = get_rss_feed_entries()
    start_date = datetime.now().astimezone() - timedelta(days=days)  # Start date for retrieval
    urls = []
    for entry in entries:
        try:
            # Convert from DATE_FORMAT to datetime
            published_at = datetime.strptime(entry.published, DATE_FORMAT).astimezone()
            if (published_at > start_date):
                urls.append(entry.link)
        except Exception as e:
            logging.error(f"Error processing entry: {entry.title} - {e}")
            continue  # Skip entries with parsing errors
    return urls


# List URLs of entries within specified days from entries based on start date
def target_update_urls(entries, start_date):
    urls = []
    for entry in entries:
        try:
            # Convert from DATE_FORMAT to datetime
            published_at = datetime.strptime(entry.published, DATE_FORMAT).astimezone()
            if (published_at >= start_date):
                urls.append(entry.link)
        except Exception as e:
            logging.error(f"Error processing entry: {entry.title} - {e}")
            continue  # Skip entries with parsing errors
    return urls


# Get articles from URL in sequence
def get_article(url):
    # Generate URL for article
    docid = docid_from_url(url)
    if docid is None:
        logging.error(f"Could not get docid from {url}.")
        return None
    link = target_url(docid)
    if link is None:
        logging.error(f"Could not get link from {url}.")
        return None

    # Set User-Agent in header for Azure Updates API
    headers = {
        "User-Agent": "Safari/605.1.15"
    }

    # Get article
    response = requests.get(link, headers=headers)
    if response.status_code != 200:
        logging.error(f"Could not get article from {link}.")
        logging.error(f"Status Code is '{response.status_code}'")
        logging.error(f"Response Message is '{response.text}'")
        return None

    return response


# Summarize article
def summarize_article(client, deployment_name, article, system_prompt=None):
    try:
        logging.debug("Starting article summarization...")
        logging.debug("Article keys: %s", article.keys() if article else 'Article is None')

        link = ", ".join(get_unique_a_href_from_html(article['description']))
        logging.debug("Extracted links: %s", link)

        content = (
            "Title: " + article['title'] + "\n"
            + "Product: " + ", ".join(article['products']) + "\n"
            + "Description: " + remove_html_tags(article['description']) + "\n"
            + "Links in description: " + link
        )
        logging.debug("Content to summarize (first 200 chars): %s...", content[:200])

        # Summarize downloaded data with Azure OpenAI
        # Use default systemprompt if system_prompt is not specified
        prompt_to_use = system_prompt if system_prompt is not None else systemprompt
        logging.debug("Using system prompt (first 100 chars): %s...", prompt_to_use[:100])
        logging.debug("Calling Azure OpenAI with deployment: %s", deployment_name)

        summary_list = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": prompt_to_use},
                {"role": "user", "content": content}
            ]
        )
        summary = summary_list.choices[0].message.content
        logging.debug("Generated summary (first 100 chars): %s...", summary[:100] if summary else 'Summary is None')

        return summary, link
    except Exception as e:
        logging.error("An error occurred during summary generation: %s", e)
        logging.error("Exception type: %s", type(e).__name__)
        logging.error("Article title: %s", article.get('title', 'N/A') if article else 'Article is None')
        import traceback
        logging.error("Traceback: %s", traceback.format_exc())
        return None


# Summarize article for table display (one sentence)
def summarize_article_for_table(client, deployment_name, article, system_prompt):
    """
    Generate a one-sentence summary of an article for table display.

    Args:
        client: Azure OpenAI client
        deployment_name: Model deployment name
        article: Article data (dict with 'title', 'products', 'description')
        system_prompt: System prompt for one-sentence summary (required)

    Returns:
        str: One-sentence summary, or None if generation fails
    """
    try:
        link = ", ".join(get_unique_a_href_from_html(article['description']))
        content = (
            "Title: " + article['title'] + "\n"
            + "Product: " + ", ".join(article['products']) + "\n"
            + "Description: " + remove_html_tags(article['description']) + "\n"
            + "Links in description: " + link
        )

        # Generate one-sentence summary with Azure OpenAI
        summary_response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )
        return summary_response.choices[0].message.content
    except Exception as e:
        logging.error("An error occurred during table summary generation: %s", e)
        return None


# Generate Azure Updates API URL
def target_url(id):
    if id is None or id == '':
        return None
    return BASE_URL + id


# Get article ID from URL
def docid_from_url(url):
    query = urlparse.urlparse(url).query
    if query is None or query == '':
        logging.error(f"Could not get query string from {url}.")
        return None

    query_list = dict(urlparse.parse_qsl(query))
    if query_list is None or query_list == '' or 'id' not in query_list:
        logging.error(f"Could not get list and id from {url}.")
        return None
    return query_list['id']


# Remove HTML tags from description
def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


# Get href from a tags in description
def get_unique_a_href_from_html(html):
    """
    Extracts unique href attributes from all <a> tags in the given HTML.

    Args:
        html (str): A string containing HTML content.

    Returns:
        list: A list of unique href attribute values from <a> tags.
    """
    soup = BeautifulSoup(html, 'html.parser')
    return list(dict.fromkeys([a['href'] for a in soup.find_all('a', href=True)]))


# Get Azure Updates article ID from URL passed as argument, make HTTP Get to Azure Updates API, and summarize the article
def read_and_summary(client, deployment_name, url, system_prompt=None):
    # Download data from URL
    response = get_article(url)
    if response is None:
        return None
    logging.debug(response.text)

    summary, link = summarize_article(client, deployment_name, response.json(), system_prompt)
    if summary is None:
        logging.error("Summary was not generated.")
        return None

    # Get article ID from URL
    docid = docid_from_url(url)
    if docid is None:
        logging.error(f"Could not get docid from {url}.")
        docid = ""
    # Remove HTML tags from description
    description = remove_html_tags(response.json()['description'])
    if description is None:
        logging.error(f"Failed to remove HTML tags from {response.json()['description']}.")
        description = response.json()['description']

    # Store title, description, and summary in retval in JSON format
    retval = {
        "url": url,
        "apiUrl": target_url(docid),
        "docId": docid,
        "title": response.json()['title'],
        "products": response.json()['products'],
        "description": description,
        "summary": summary,
        "publishedDate": response.json()['created'],
        "updatedDate": response.json()['modified'],
        "referenceLink": link
    }
    logging.debug(retval)

    return retval


def main():
    from dotenv import load_dotenv

    load_dotenv()

    # Log configuration
    logging.basicConfig(force=True, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if len(sys.argv) > 1 and (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print("Usage: cp .env.template .env; python azureupdatehelper.py")
        return
    # Get command line arguments
    # python azureupdatehelper.py [--days 7]
    if len(sys.argv) > 2 and sys.argv[1] == "--days":
        global DAYS
        DAYS = int(sys.argv[2])

    print("Checking environment variables...")
    # Display error and exit if environment variables are missing
    if not environment_check():
        logging.error('Environment variables are missing. Please check the .env file.  (環境変数が不足しています。.env ファイルを確認してください。)')
        return
    print("Environment variables OK.")
    client, deployment_name = azure_openai_client(os.getenv("API_KEY"), os.getenv("API_ENDPOINT"))
    print("Client: ", client)
    entries = get_rss_feed_entries()
    print(f"RSS feed has {len(entries)} entries.")
    start_date = datetime.now().astimezone() - timedelta(days=DAYS)
    print(f"Start date: {start_date.strftime('%Y-%m-%d')}")
    urls = target_update_urls(entries, start_date)
    print(f"There are {len(urls)} Azure updates.")
    print('The included Azure Updates URLs are as follows:')
    print(urls)
    for url in urls:
        result = read_and_summary(client, deployment_name, url)
        if result is None:
            continue
        print("--------------------")
        for key, value in result.items():
            print(f"{key}: {value}")
            print()
        print("--------------------")


if __name__ == "__main__":
    main()
