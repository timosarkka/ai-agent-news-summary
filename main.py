# Import libraries
import yaml
from smolagents import CodeAgent, OpenAIModel
from tools.news_tools import latest_news
from tools.final_answer import final_answer

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# Define the model to be used
model = OpenAIModel(
    model_id="o4-mini-high",
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
    domain = input("Enter the news domain (e.g. hs.fi, yle.fi, bbc.com): ").strip()
    user_query = f"Fetch the latest news headlines from {domain} and summarize today's most important stories."
    summary = agent.run(user_query)
    print(summary)