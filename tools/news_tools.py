# Import libraries
from bs4 import BeautifulSoup
import configparser
import logging
import requests
import json
from newspaper import Article
from smolagents import tool

# Load API key
config = configparser.ConfigParser()
config.read('config.ini')
news_apikey = config['credentials']['news_apikey']

@tool
def latest_news(domainurl: str) -> str:
    """
    Fetches the 10 latest news headlines and URLs from the specified domain.
    Args:
        domainurl: The news site’s domain, e.g. "bbc.com" or "yle.fi".
    Returns:
        A JSON‐string of a list of {"title": ..., "url": ...} dictionaries.
    """
    url = f'https://newsdata.io/api/1/latest?apikey={news_apikey}&domainurl={domainurl}'
    response = requests.get(url)
    data = response.json().get("results", [])
    headlines_list = []
    for article in data[:10]:
        dict = {"title": article["title"], "url": article["link"]}
        headlines_list.append(dict)
    return headlines_list

@tool
def fetch_article_text(url: str) -> str:
    """
    Downloads and parses the contents of a news article with newspaper3k.
    Args:
        url (str):
            The full URL of the news article to fetch.
    Returns:
        str:
            The extracted article text. If newspaper3k fails (e.g. paywall,
            parsing error), falls back to extracting all `<p>` tag text
            via BeautifulSoup.
    """
    try:
        art = Article(url)
        art.download()
        art.parse()
        return art.text
    except Exception as e:
        logging.warning(f"Extracting with newspaper3k failed for {url}: {e}")
        logging.warning("Trying with BeautifulSoup instead...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n\n".join(p.get_text(strip=True) for p in paragraphs)