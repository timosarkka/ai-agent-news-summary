# Import libraries
from bs4 import BeautifulSoup
import configparser
import logging
import requests
import json
from newspaper import Article
from smolagents import tool, CodeAgent, OpenAIServerModel

# Get credentials from config
config = configparser.ConfigParser()
config.read('config.ini')
news_apikey = config['credentials']['news_apikey']
openai_apikey = config['credentials']['openai_apikey']

# Instantiate the smolagents wrapper around OpenAI
_model = OpenAIServerModel(
    model_id="gpt-4.1-nano",
    api_base="https://api.openai.com/v1",
    api_key=openai_apikey,
    temperature=0.3,
    max_tokens=2048
)

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
    
@tool
def summarize_articles(articles: list[dict], max_length: int = 500) -> list[dict]:
    """
    Given a list of {"title":…, "url":…, "text":…}, produce
    {"title", "url", "summary"} for each via LLM.
    Args:
        articles (list[dict]): Each dict must have keys 'title', 'url', and
            'text' (the full article body).
        max_length (int, optional): Max words in the generated summary. Defaults to 500.

    Returns:
        list[dict]: One dict per article, with 'title', 'url', and
            the LLM‐generated 'summary'.
    """
    summaries = []
    for art in articles:
        prompt = (
            f"Please write a concise but detailed summary of the following news article:\n\n"
            f"Title: {art['title']}\nURL: {art['url']}\n\n"
            f"Article text:\n{art['text']}\n\n"
            f"Summary (max {max_length} words):"
        )

        # Call the model via smolagents
        response = _model.chat_completion(  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(max_length * 1.5),
        )
        # Extract just the text of the assistant’s reply
        summary_text = response.choices[0].message.content.strip()

        summaries.append({
            "title":   art["title"],
            "url":     art["url"],
            "summary": summary_text
        })

    return summaries