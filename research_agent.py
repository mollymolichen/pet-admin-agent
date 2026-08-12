"""Minimal Deep Agent research example using the GitHub Copilot API Gateway.

The gateway exposes an OpenAI-compatible API at http://127.0.0.1:3030/v1,
so we configure both the direct OpenAI client and the LangChain model to use it.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI

from deepagents import create_deep_agent

load_dotenv()

# The Copilot API Gateway exposes a curated model list; gpt-4o is not valid here.
DEFAULT_MODEL = os.getenv("DEEPAGENT_MODEL", "gpt-5")
GATEWAY_BASE_URL = os.getenv(
    "GITHUB_COPILOT_API_GATEWAY_BASE_URL", "http://127.0.0.1:3030/v1"
)
GATEWAY_API_KEY = os.getenv("GITHUB_COPILOT_API_GATEWAY_API_KEY", "optional")


def gateway_client() -> OpenAI:
    return OpenAI(base_url=GATEWAY_BASE_URL, api_key=GATEWAY_API_KEY)


def gateway_healthcheck() -> str:
    response = gateway_client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Hello!"}],
    )
    return response.choices[0].message.content or ""


def get_search_tool(model_name: str):
    """Return the provider-native built-in web search tool for the selected model."""
    provider = model_name.split(":", 1)[0].lower() if ":" in model_name else "openai"

    if provider == "anthropic":
        return {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
    if provider in {"openai", "gpt"}:
        return {"type": "web_search"}
    if provider in {"google", "google_genai"}:
        return {"google_search": {}}

    raise ValueError(
        "Unsupported provider. Use one of: anthropic, openai, google_genai. "
        f"Received: {model_name}"
    )


research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""


llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    temperature=0,
)

search_tool = get_search_tool(DEFAULT_MODEL)
agent = create_deep_agent(
    model=llm,
    tools=[search_tool],
    system_prompt=research_instructions,
)

if __name__ == "__main__":
    print("Gateway check:", gateway_healthcheck())
    user_question = "What is LangGraph?"
    result = agent.invoke({"messages": [{"role": "user", "content": user_question}]})
    print(result["messages"][-1].content)
