import requests

# Make API call and fetch the 5 latest news headlines, and their urls from yle.fi
def latest_finnish_news():
    url = 'https://newsdata.io/api/1/latest?apikey=pub_847374e14bb4cd7c4a8b8a6a4c4e48a29f651&domainurl=yle.fi'
    response = requests.get(url)
    print(response.text)

latest_finnish_news()

# Next, scrape the full content of aforementioned articles and save somewhere for later processing by LLM