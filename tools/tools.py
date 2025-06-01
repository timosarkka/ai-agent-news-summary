# Import libraries
from bs4 import BeautifulSoup
import configparser
import logging
import requests
import json
import smtplib
from newspaper import Article
from smolagents import tool, CodeAgent, OpenAIServerModel
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get credentials from config
config = configparser.ConfigParser()
config.read('config.ini')
news_apikey   = config['credentials']['news_apikey']
openai_apikey = config['credentials']['openai_apikey']

# Instantiate the smolagents wrapper around OpenAI
_model = OpenAIServerModel(
    model_id   = "gpt-4.1-nano",
    api_base   = "https://api.openai.com/v1",
    api_key    = openai_apikey,
    temperature= 0.3,
    max_tokens = 2048
)

@tool
def latest_news(domainurl: str) -> str:
    """
    Fetches the 10 latest news headlines and URLs from the specified domain.
    Args:
        domainurl (str): The news site’s domain, e.g. "bbc.com" or "yle.fi".
    Returns:
        str: A JSON‐string of a list of {"title": ..., "url": ...} dictionaries.
    """
    url = f'https://newsdata.io/api/1/latest?apikey={news_apikey}&domainurl={domainurl}'
    response = requests.get(url)
    data = response.json().get("results", [])
    headlines_list = []
    for article in data[:10]:
        d = {"title": article["title"], "url": article["link"]}
        headlines_list.append(d)
    return headlines_list

@tool
def fetch_article_text(url: str) -> str:
    """
    Downloads and parses the contents of a news article with newspaper3k.
    Args:
        url (str): The full URL of the news article to fetch.
    Returns:
        str: The extracted article text.
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
def summarize_articles(articles: list[dict], max_length: int = 100) -> list[dict]:
    """
    Given a list of articles (with title, url, and text), produce an LLM-powered summary for each.
    Args:
        articles (list[dict]): A list of dictionaries, each containing "title", "url", and "text".
        max_length (int, optional): The maximum word length for each summary. Defaults to 500.
    Returns:
        list[dict]: A list of dictionaries, each with "title", "url", and "summary".
    """
    summaries = []
    for art in articles:
        prompt = (
            f"Please write a concise but detailed summary of the following news article:\n\n"
            f"Title: {art['title']}\nURL: {art['url']}\n\n"
            f"Article text:\n{art['text']}\n\n"
            f"Summary (max {max_length} words):"
        )
        message = _model(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=int(max_length * 1.5),
        )
        summary_text = message.content.strip()
        summaries.append({
            "title":   art["title"],
            "url":     art["url"],
            "summary": summary_text
        })
    return summaries

@tool
def generate_summary(domainurl: str) -> str:
    """
    Produces a nicely formatted summary (~500 words) by:
      1) Fetching latest headlines via `latest_news`.
      2) Downloading each article’s text via `fetch_article_text`.
      3) Summarizing each individually via `summarize_articles`.
      4) Concatenating these mini-summaries and asking the LLM to reformat into
         short paragraphs and bullet points.
    Args:
        domainurl (str): The news site’s domain, e.g. "bbc.com" or "yle.fi".
    Returns:
        str: The final unified summary, formatted with paragraphs & bullets.
    """
    # 1) Get up to 10 latest headlines + URLs
    headlines = latest_news(domainurl)
    
    # 2) Fetch full text for each headline
    articles = []
    for item in headlines:
        body = fetch_article_text(item["url"])
        articles.append({
            "title": item["title"],
            "url":   item["url"],
            "text":  body
        })
    
    # 3) Summarize each article (max 100 words each)
    summaries = summarize_articles(articles, max_length=100)
    
    # 4) Combine all individual summaries into one block
    combined_text = "\n\n".join(s["summary"] for s in summaries)
    
    # 5) Ask the LLM to reformat combined_text into short paragraphs + bullet points
    formatting_prompt = (
        f"Below are concise summaries of today’s top articles:\n\n"
        f"{combined_text}\n\n"
        "Please transform this into a final summary of about 500 words, "
        "using short paragraphs and bullet points so it’s easy to read. "
        "Include headlines or key points as bullets where appropriate."
        "If you're in danger of running out of tokens/space, don't include any sentences that are cut off from the middle!"
    )
    message = _model(
        messages=[{"role": "user", "content": formatting_prompt}],
        max_tokens=300
    )
    formatted_summary = message.content.strip()
    return formatted_summary

@tool
def send_email(subject: str, body: str) -> None:
    """
    Sends a plain-text email using SMTP parameters from [email] in config.ini.
    Args:
        subject (str): The email’s subject line.
        body (str): The email’s body (plain text).
    Returns:
        None
    """
    # Read the [email] section
    email_cfg = config["email"]
    smtp_server  = email_cfg["smtp_server"]
    smtp_port    = int(email_cfg["smtp_port"])
    username     = email_cfg["smtp_username"]
    password     = email_cfg["smtp_password"]
    from_addr    = email_cfg["from_address"]
    to_addr      = email_cfg["to_address"]

    # Compose MIME message
    msg = MIMEMultipart()
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send via TLS
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()