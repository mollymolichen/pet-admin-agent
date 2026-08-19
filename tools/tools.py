"""JSON-backed storage for pets and their admin tasks (vaccinations, appointments, meds, etc.)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any
from langchain.tools import tool

DATA_FILE = Path(__file__).with_name("pet_data.json")

TASK_CATEGORIES = ["vaccination", "appointment", "medication", "grooming", "other"]

'''
This file contains tools to manage pets and their associated tasks. 
These tools are used by the agent to perform operations such as listing pets, adding new pets, listing tasks, adding tasks, marking tasks as done, and deleting pets or tasks. 
The data is stored in a JSON file for persistence.
'''

def _empty_state() -> dict[str, Any]:
    return {"pets": [], "tasks": {}}

def _load() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return _empty_state()
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def _save(state: dict[str, Any]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)

# Tool to list all pets in the household, used by the agent.
@tool(parse_docstring=True)
def list_pets() -> list[dict[str, Any]]:
    """List all pets in the household."""
    state = _load()
    if (len(state["pets"])) == 0:
        print("No pets found in the household.")
        return []
    else:
        print(f"Listing all {len(state['pets'])} pets in the household:")
        for index, pet in enumerate(state["pets"], start=1):   
            print(f"  {index}. {pet['name']} ({pet['species']}), breed: {pet.get('breed', 'unknown')}, birthday: {pet.get('birthdate', 'unknown')}, notes: {pet.get('notes', 'none')}")
    return state["pets"]

# Internal function to get a pet by name, used by the agent.
def get_pet_by_name(name: str) -> dict[str, Any] | None:
    state = _load()
    for pet in state["pets"]:
        if pet["name"].lower() == name.lower():
            print(f"Found pet: {pet['name']} ({pet['species']})")
            return pet
    return None

# Tool to add a pet, used by the agent.
@tool(parse_docstring=True)
def add_pet(
    name: str, species: str, memorialize: bool, breed: str = "", birthdate: str = "", notes: str = ""
) -> dict[str, Any]:
    """Add a new pet (dog or cat) to the household.

    Args:
        name: The pet's name.
        species: "dog" or "cat".
        memorialize: Whether to memorialize the pet (e.g., if deceased).
        breed: Optional breed.
        birthdate: Optional birthdate in YYYY-MM-DD format.
        notes: Optional free-text notes about the pet.
    """
    state = _load()
    pet_id = str(uuid.uuid4())
    pet = {
        "id": pet_id,
        "name": name,
        "species": species,
        "memorialize": memorialize,
        "breed": breed,
        "birthdate": birthdate,
        "notes": notes,
    }
    state["pets"].append(pet)
    _save(state)
    print(f"Congratulations on your new pet! I've added {pet['name']} to your household.")
    return pet

# Tool to delete a pet, used by the agent.
@tool(parse_docstring=True)
def delete_pet(pet_id: str) -> bool:
    """Delete a pet and all of its associated tasks.

    Args:
        pet_id: The unique ID of the pet to remove.
    """
    state = _load()
    if pet_id not in state["pets"]:
        return False
    del state["pets"][pet_id]
    state["tasks"] = {
        tid: t for tid, t in state["tasks"].items() if t["pet_id"] != pet_id
    }
    _save(state)
    print(f"Pet with ID {pet_id} has been deleted, along with any associated tasks.")
    return True

# Tool to list tasks, used by the agent.
@tool(parse_docstring=True)
def list_tasks(
    pet_name: str | None = None,
    category: str | None = None,
    include_done: bool = True,
) -> list[dict[str, Any]]:
    """List admin tasks (vaccinations, appointments, medications, grooming, etc.).

    Args:
        pet_name: Optional pet name to filter by.
        category: Optional category filter: vaccination, appointment, medication, grooming, other.
        include_done: Whether to include tasks already marked done.
    """
    state = _load()
    pet_id = None
    if pet_name:
        pet = get_pet_by_name(pet_name)
        if pet is None:
            return []
        pet_id = pet["id"]

    tasks = list(state["tasks"])
    if pet_id:
        tasks = [t for t in tasks if t["pet_id"] == pet_id]
    if category:
        tasks = [t for t in tasks if t["category"] == category]
    if not include_done:
        tasks = [t for t in tasks if not t["done"]]

    tasks.sort(key=lambda t: (t["done"], t.get("due_date") or "9999-99-99"))
    for index, task in enumerate(tasks, start=1):
        status = "Done" if task["done"] else "Pending"
        due = task.get("due_date", "no due date")
        print(f"  {index}. [{status}] {task['title']} for {task['pet_name']} (category: {task['category']}, due: {due})")

    return tasks

# Tool to add a task, used by the agent.
@tool(parse_docstring=True)
def add_task(
    pet_name: str,
    category: str,
    title: str,
    due_date: str = "",
    notes: str = "",
) -> dict[str, Any]:
    """Add an admin task for a pet, such as a vaccination, vet appointment, medication, or grooming visit.

    Args:
        pet_name: The name of the pet this task is for. The pet must already exist.
        category: One of vaccination, appointment, medication, grooming, other.
        title: Short description of the task, e.g. "Rabies booster" or "Annual checkup".
        due_date: Optional due date in YYYY-MM-DD format.
        notes: Optional additional notes.
    """
    if category not in TASK_CATEGORIES:
        raise ValueError(f"category must be one of {TASK_CATEGORIES}")

    pet = get_pet_by_name(pet_name)
    if pet is None:
        raise ValueError(f"No pet named '{pet_name}' found. Add the pet first.")

    state = _load()
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "pet_id": pet["id"],
        "pet_name": pet["name"],
        "category": category,
        "title": title,
        "due_date": due_date,
        "notes": notes,
        "done": False,
    }
    state["tasks"].append(task)
    _save(state)

    print(f"Added task '{title}' for {pet['name']} (category: {category}, due: {due_date or 'no due date'}).")
    return task

# Tool to mark a task as done or not done, used by the agent.
@tool(parse_docstring=True)
def mark_task_done(task_id: str, done: bool = True) -> dict[str, Any] | None:
    """Mark an admin task as done (or not done).

    Args:
        task_id: The id of the task to update.
        done: True to mark complete, False to reopen it.
    """
    state = _load()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        print(f"No task with ID {task_id} found.")
        return None
    task["done"] = done
    _save(state)

    print(f"Task '{task['title']}' for {task['pet_name']} marked as {'done' if done else 'not done'}.")
    return task

# Tool to delete a task, used by the agent.
@tool(parse_docstring=True)
def delete_task(task_id: str) -> bool:
    """Delete one admin task by its unique ID.

    Args:
        task_id: The unique ID of the task to remove.
    """
    state = _load()
    task = next((t for t in state["tasks"] if t["id"] == task_id), None)
    if task is None:
        print(f"No task with ID {task_id} found.")
        return False
    state["tasks"].remove(task)
    _save(state)

    print(f"Task with ID {task_id} has been deleted.")
    return True
