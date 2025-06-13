# News Summary Agent

## 1. Introduction

This is a lightweight Python-based AI agent that searches for the latest news from any news domain, reads the articles and generates a concise daily news summary using an LLM. Currently, I'm using **gpt-4.1-nano** model for the summarizing. The agent framework I'm using is [smolagents](https://github.com/huggingface/smolagents).

The reason for building this agent is to **get a daily news summary twice a day to my email**, if I'm too busy to actually read the news. This is surprisingly difficult to do with the basic LLM models today via the chat UIs. Often, they will not provide the latest news, will hallucinate news pieces or just get blocked by the news sites. I'm sure future agentic models like the [Operator](https://openai.com/index/introducing-operator/) will fix this, but meanwhile, why not code my own solution?

The original template used to build this agent was kindly provided by [Hugging Face](https://huggingface.co/spaces/agents-course/First_agent_template).

## 2. Main Features

When executing the agent in its normal automated mode, it goes searching for news articles from a domain preset by the user in config.ini.

For example, [hs.fi](https://hs.fi), [yle.fi](https://yle.fi), [bbc.com](https://bbc.com), [nytimes.com](https://nytimes.com), or any other major news outlet that can be used by the [newsdata.io API](https://newsdata.io/).

As an output, it sends an approximately 600-word long daily news summary for the user via email.

Under the hood, the agent independently uses **5 separate tools** that it has access to:

- **Tool #1**: Fetches the latest news headlines and their urls using newsdata.io API
- **Tool #2**: Scrapes the actual news article content with newspaper3k/BeautifulSoup -libraries
- **Tool #3**: Summarizes each article and stores it into a list of dictionaries
- **Tool #4**: A grouping tool that lets the agent execute tools 1-3 in a simplified fashion via the scheduler.py
- **Tool #5**: Sends the news summary/analysis via email 

The summarizing behavior can be fined-tuned by altering the user query used in main.py.

### 2.1 Example of usage in automated mode

Each day, twice a day, the agent provides a news summary at 8.00 am and 4.00 pm. Currently I'm running the agent from a dedicated small Linux VM hosted on Azure.

A part of an example news summary from 8.6.2024, the news domain set at [yle.fi](https://yle.fi). The time of the piece is different than normally since I was testing the agent, but the actual daily news summaries provided are identical to the one in the screenshot:

![E72E8442-229F-46C7-8372-BCB62A10D32F](https://github.com/user-attachments/assets/7af1f4f7-2aa4-4856-b519-663e88cecf01)

The full summaries are usually about 600-700 words long and include a wide variety of different topics.

### 2.2 Example of usage in manual mode

The agent can also be used manually from the command line. Then the agent prompts for the news domain url from the user. An intriguing characteristic of the agent is that it sometimes fails to execute its internal code, logs an error but finds a way to carry on nevertheless (this is a phenomenon called ["self-healing"](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-09-compact-errors.md)).

An example manual run from the command line:
\
\
<img src="docs/newsaiagent_demo.gif" alt="Demo run of the News Summary AI Agent" width="900"/>

## 3. Main Architecture

The basic architecture of the agent is currently as follows:

1. **main.py**  
   - Loads API keys and prompt templates  
   - Instantiates a smolagents CodeAgent with the necessary tools
   - Prompts the user for a news domain and kicks off the agent loop
  
2. **scheduler.py**
   - A standalone script that uses the schedule library to run a “job” at 08:00 and 16:00 every day.
   - The job() function simply calls generate_summary(domain) (where domain is read from config.ini) and then send_email(...) to deliver the formatted news summary twice daily.
   - Keeps running in a while True: schedule.run_pending() loop to trigger the email automatically on schedule

3. **tools.py**
   - **latest_news(domainurl)**: fetches recent headlines via the NewsData API from the given domainurl
   - **fetch_article_text(url)**: fetches the article texts from the urls
   - **summarize_articles(articles, max_length)**: summarizes the article texts, the model reads at most max_length words for the summary
   - **generate_summary(domainurl)**: Runs the entire pipeline—calls latest_news → fetch_article_text → summarize_articles on each article, then combines all mini-summaries and asks the LLM to distill them into a ~600-word, nicely formatted summary (paragraphs + bullet points)
   - **send_email(subject, body)**: Sends a plain-text email (using SMTP credentials from config.ini) with the given subject and body
   - **final_answer.py** → formats and returns the LLM’s news summary (mainly used when executing manually from CLI)

4. **Agent Loop** (smolagents)  
   - **Think**: LLM plans next step  
   - **Act**: Calls tools as necessary to achieve the desired goals
   - **Observe**: Observers the result of the latest action
   - **Think**: Plans next step, and so on...
  
## 4. Tech Stack

- **Python**: Main language for the agent and tools. Libraries used include configparser, yaml, requests, json, newspaper3k, smtplib etc.
- **smolagents**: Framework used for the agent itself and its orchestration  
- **LLMs**: OpenAI Python SDK, gpt-4.1-nano model used via the OpenAI API for summary generation

## 5. Project Structure

The project files and folders are structured as shown below. **Note that I have not provided config.ini itself for security reasons**, but this is just a standard config-setup, so it should be quite straightforward to build on your own.

```
ai-agent-news-summary
├── tools/
│   ├── final_answer.py     # Allows the agent to form the final answer
|   ├── tools.py            # Contains the tools
|   ├── __init__.py         # This is needed so that the folder is recognized as a package
├── agent.json              # Contains the basic agent definition, including model, tools, prompt_templates, authorized imports
├── config.ini              # Config loader
├── main.py                 # The actual script used to run the agent, mainly contains a basic model and agent definition
├── prompts.yaml            # System prompts that give examples for the agent to help reasoning and break down tasks
├── scheduler.py            # Contains the scheduling logic to run the agent
├── README.md               # This readme-file
└── requirements.txt        # All libraries and imports needed to run the agent
```
