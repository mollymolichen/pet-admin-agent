"""Deep Agent configured as a pet admin assistant, using the GitHub Copilot API Gateway."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from managed_deepagents import define_deep_agent
from tools.tools import add_pet, add_task, delete_task, list_pets, list_tasks, mark_task_done

load_dotenv()

DEFAULT_MODEL = os.getenv("DEEPAGENT_MODEL", "gpt-5.5")
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

llm = ChatOpenAI(
    model=DEFAULT_MODEL
    #base_url=GATEWAY_BASE_URL,
    #api_key=GATEWAY_API_KEY,
    #temperature=0,
)

agent = define_deep_agent(
    name="pet-admin-assistant",
    model=llm,
    tools=[list_pets, add_pet, list_tasks, add_task, mark_task_done, delete_task, _search_tool_for(DEFAULT_MODEL)],
)

'''
Implement interactive input() prompts in pet_agent.py only if you want a form-like command-line experience. 
For the current agent-chat approach, keep prompting conversationally through the agent rather than adding prompts inside pet_store.py.
Example:
    agent = create_deep_agent(
        model=llm,
        tools=[add_pet],
        system_prompt=pet_admin_instructions,
    )

    result = agent.invoke({
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

def onboard_agent():
    """Onboard the user to the pet admin assistant."""
    print("Welcome to the Pet Admin Assistant!")
    print("I can help you manage your pets and tasks.")
    print("Let's get started with some basic information about your pets.")
    # Here you can add more onboarding steps, such as asking for pet names, types, etc.
    pet_name = input("Please enter the name of your pet: ").strip()
    pet_species = input(f"Aww, {pet_name} is such a cute name! What species is {pet_name}? ").strip()
    pet_age = input(f"How old is {pet_name}? ").strip()
    pet_breed = input(f"What breed is {pet_name}? ").strip()
    print(f"Great! You've added {pet_name}, a {pet_age}-year-old {pet_breed} {pet_species}.")   # TODO: Standardize breed and species
    print("Now, let's see what tools I can help you with.")

    for index, tool_name in enumerate(TOOL_CHOICES, start=1):
        print(f"  {index}. {tool_name}")

if __name__ == "__main__":
    onboard_agent()