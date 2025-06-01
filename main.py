# Import libraries
import configparser
import yaml
from smolagents import CodeAgent, OpenAIServerModel
from tools.tools import latest_news, fetch_article_text, summarize_articles
from tools.final_answer import FinalAnswerTool

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# Get credentials from config
config = configparser.ConfigParser()
config.read('config.ini')
openai_apikey = config['credentials']['openai_apikey']

# Define final answer
final_answer = FinalAnswerTool()

# Define the model to be used
model = OpenAIServerModel(
    model_id="gpt-4.1-nano",                            
    api_base="https://api.openai.com/v1",         
    api_key=openai_apikey,
    temperature=0.5,
    max_tokens=2096
)

# Define agent  
agent = CodeAgent(
    model=model,
    tools=[latest_news, fetch_article_text, summarize_articles, final_answer],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates
)

# Run the agent
if __name__ == "__main__":
    domain = input("Enter the news domain url. It can be any major news source (e.g. hs.fi, yle.fi, is.fi, il.fi, bbc.com, nytimes.com, reuters.com): ").strip()
    user_query = f"Fetch the latest news headlines and their urls from {domain}. Then proceed to extract the actual news article texts behind the urls. Summarize these article texts into individual summaries, then combine them into one big unified summary, and return one final summary to the user which is max. 125 words long. Please prioritize technology, AI and business -themed articles in the summary if they are available. Use natural language, don't include any direct urls. Don't use meta phrases like 'The article covers...', or 'The news today cover a wide range of topics...'. Just summarize the actual contents concisely and briefly. Try to omit opinion pieces from the summary, if they are part of your scraped data. I want you to focus more on factual events that have happened in the world."
    summary = agent.run(user_query)
    print(summary)