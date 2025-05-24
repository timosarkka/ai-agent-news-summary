# AI News Summary Agent

## 1. Introduction

This is a lightweight Python-based AI agent that searches for the latest news from any news domain, reads the articles and generates a concise daily news summary using an LLM. Currently, I'm using **gpt-4.1-nano** model for the summarizing. The agent framework I'm using is [smolagents](https://github.com/huggingface/smolagents).

**This repo is a work-in-progress**, I will keep adding features as I learn how to build cool stuff.

The original template used to build this agent was kindly provided by [Hugging Face](https://huggingface.co/spaces/agents-course/First_agent_template).

## 2. Main Features

When executing the tool manually, it asks for a news website domain url from the user (for example, [hs.fi](https://hs.fi), [yle.fi](https://yle.fi), [bbc.com](https://bbc.com), [nytimes.com](https://nytimes.com), [reuters.com](https://reuters.com) or any other major news outlet that can be used by the [newsdata.io API](https://newsdata.io/)) and as an output, returns an approximately 125-word long daily news analysis for the user.

Example of manual usage from the command line:
\
\
\
<img src="https://github.com/user-attachments/assets/2105dc99-f990-4995-8916-adb5cfd40140" width="800">
\
\
\
Later on, I want to add the following extra features to the agent:

- Analyze the actual news pieces behind the urls and provide a more detailed summary based on the key points
- Highlight the news pieces from themes that are of special relevance to me personally: e.g. tech, AI, politics
- Schedule the agent to provide the summary via email every morning and afternoon at 8.00 am / 4.00 pm

## 3. Project Structure

The project files and folders are structured as shown below. **Note that I have not provided config.ini itself for security reasons**, but this is just a standard config-setup, so it should be quite straightforward to build on your own.

For more elaboration on the actual **agent architecture**, please see section 5.

```
ai-agent-news-summary
├── tools/
│   ├── final_answer.py     # Allows the agent to form the final answer
|   ├── news_tools.py       # Contains the tools for extracting headlines and news via newsdata.io API
|   ├── __init__.py         # This is needed so that the folder is recognized as a package
├── agent.json              # Contains the basic agent definition, including model, tools, prompt_templates, authorized imports
├── config.ini              # Config loader
├── main.py                 # The actual script used to run the agent, mainly contains a basic model and agent definition
├── prompts.yaml            # System prompts that give examples for the agent to help reasoning and break down tasks
├── README.md               # This readme-file
└── requirements.txt        # All libraries and imports needed to run the agent
```

## 4. Tech Stack

- **Python**: Main language for the agent and tools. Libraries used include configparser, yaml, requests, json
- **smolagents**: Framework used for the agent itself and its orchestration  
- **LLMs**: OpenAI Python SDK, gpt-4.1-nano model used via the OpenAI API for summary generation

## 5. Main Architecture

The basic architecture of the agent is currently as follows:

1. **main.py**  
   - Loads API keys and prompt templates  
   - Instantiates a smolagents CodeAgent with the necessary tools
   - Prompts the user for a news domain and kicks off the agent loop  

2. **Tools**  
   - **news_tools.py** → `latest_news(domainurl)`: fetches recent headlines via the NewsData API from the given domainurl
   - **final_answer.py** → formats and returns the LLM’s news summary 

3. **Agent Loop** (smolagents)  
   - **Think**: LLM plans next step  
   - **Act**: calls `latest_news` to get headlines  
   - **Observe**: ingests headline data  
   - **Think**: LLM writes a one-paragraph summary  
   - **Act**: calls `final_answer` to output the result
