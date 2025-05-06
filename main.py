# Import libraries
import configparser
import yaml
from smolagents import CodeAgent, OpenAIServerModel
from tools.news_tools import latest_news
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
    tools=[latest_news, final_answer],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates
)

# Run the agent
if __name__ == "__main__":
    domain = input("Enter the news domain url. It can be any major news source (e.g. hs.fi, yle.fi, is.fi, il.fi, bbc.com, nytimes.com): ").strip()
    user_query = f"Fetch the latest news headlines from {domain} and summarize today's most important stories. The summary should consist of one paragraph that has the key points summarized in natural language, but don't include any urls."
    summary = agent.run(user_query)
    print(summary)