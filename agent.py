"""Deep Agent configured as a pet admin assistant, using the GitHub Copilot API Gateway."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from managed_deepagents import define_deep_agent
from pet_store import add_pet, add_task, delete_task, list_pets, list_tasks, mark_task_done

load_dotenv()

DEFAULT_MODEL = os.getenv("DEEPAGENT_MODEL", "gpt-5")
GATEWAY_BASE_URL = os.getenv(
    "GITHUB_COPILOT_API_GATEWAY_BASE_URL", "http://127.0.0.1:3030/v1"
)
GATEWAY_API_KEY = os.getenv("GITHUB_COPILOT_API_GATEWAY_API_KEY", "optional")
# Provider-native web search, matched to the configured model family.
_SEARCH_TOOLS = {
    "anthropic": {"type": "web_search_20260209", "name": "web_search", "max_uses": 5},
    "gpt": {"type": "web_search"},
    "google": {"google_search": {}},
}
TOOL_CHOICES = (
    "list_pets",
    "add_pet",
    "list_tasks",
    "add_task",
    "mark_task_done",
    "internet_search",
)

def _search_tool_for(model_name: str) -> dict:
    lower = model_name.lower()
    for prefix, tool in _SEARCH_TOOLS.items():
        if lower.startswith(prefix):
            return tool
    return _SEARCH_TOOLS["gpt"]


pet_admin_instructions = (
    Path(__file__).with_name("pet_admin.md").read_text(encoding="utf-8").strip()
)

llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    temperature=0,
)

'''
Implement interactive input() prompts in pet_agent.py only if you want a form-like command-line experience. 
For the current agent-chat approach, keep prompting conversationally through the agent rather than adding prompts inside pet_store.py.
Example:
    selected_agent = create_deep_agent(
        model=llm,
        tools=[add_pet],
        system_prompt=pet_admin_instructions,
    )

    result = selected_agent.invoke({
        "messages": [{
            "role": "user",
            "content": (
                "Add Luna, a dog. Breed: Labrador. "
                "Birthdate: 2022-05-01. Memorialize: false."
            ),
        }],
        "selected_tool": "add_pet",
    })
'''
def create_agent() -> None:
    # TODO: Instead of asking the user to set up from scratch, ask them for some background on their pets before onboarding.
    selection = input("Hello! I'm your pet admin assistant. I can help you manage your pets and tasks. What would you like help with today? ").strip()
    for index, tool_name in enumerate(TOOL_CHOICES, start=1):
        print(f"  {index}. {tool_name}")

    # The following is an alternative approach using managed deep agents for easier deployments.
    selected_agent = define_deep_agent(
        name="pet-admin-assistant",
        model=llm,
        tools=[list_pets, add_pet, list_tasks, add_task, mark_task_done, delete_task, _search_tool_for(DEFAULT_MODEL)],
    )

    selected_agent.invoke({
        "messages": [{"role": "user", "content": selection}]
    })

if __name__ == "__main__":
    create_agent()