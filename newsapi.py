# Import libraries
import configparser
import requests
import pandas as pd

# Load configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get credentials from config
nd = config['newsdata']
apikey = nd['apikey']

# Make API call and fetch the 10 latest news headlines, and their urls
def latest_finnish_news(domainurl):
    url = f'https://newsdata.io/api/1/latest?apikey={apikey}&domainurl={domainurl}'
    response = requests.get(url)

    # Process the result of API call, if call successful
    if response.status_code == 200:
        data = response.json()
        headlines_list = []
        for article in data.get("results", []):
            headlines_list.append((article["title"], article["link"]))
    else:
        print(f"Error: {response.status_code}, {response.text}")

    # Convert to dataframe
    df = pd.DataFrame(headlines_list)
    pd.set_option('display.max_rows', None, 'display.max_columns', None)
    print(df)

def main():
    domainurl = "hs.fi"
    latest_finnish_news(domainurl)

main()