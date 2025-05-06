# Import libraries
import configparser
import requests
import json
from smolagents import tool

# Load API key
config = configparser.ConfigParser()
config.read('config.ini')
apikey = config['newsdata']['apikey']

@tool
def latest_news(domainurl: str) -> str:
    # Fetches the 10 latest news headlines and URLs from the specified domain.
    # Returns a JSON string of a list of {"title": ..., "url": ...}.
    url = f'https://newsdata.io/api/1/latest?apikey={apikey}&domainurl={domainurl}'
    response = requests.get(url)
    data = response.json().get("results", [])
    headlines_list = []
    for article in data[:10]:
        dict = {"title": article["title"], "url": article["link"]}
        headlines_list.append(dict)
    return json.dumps(headlines_list)