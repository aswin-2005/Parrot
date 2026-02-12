from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------
# DATE HELPERS
# -------------------------

def to_display_date(db_date: str | None) -> str | None:
    if not db_date:
        return None

    try:
        parsed = datetime.strptime(db_date, "%Y-%m-%d")
        return parsed.strftime("%a-%d/%b/%y")
    except ValueError:
        return db_date


# -------------------------
# GET TASKS
# -------------------------

def get_tasks():
    response = supabase.table("Tasks").select("*").order("id").execute()

    tasks = response.data or []

    # Convert DB date to display format
    for task in tasks:
        if task.get("due_date"):
            task["due_date"] = to_display_date(task["due_date"])

    return tasks


# -------------------------
# TOGGLE TASK
# -------------------------

def toggle_task(task_id: int):
    task = supabase.table("Tasks") \
        .select("completed") \
        .eq("id", task_id) \
        .single() \
        .execute()

    if not task.data:
        return False

    new_status = not task.data["completed"]

    supabase.table("Tasks") \
        .update({"completed": new_status}) \
        .eq("id", task_id) \
        .execute()

    return True


# -------------------------
# ADD TASK
# -------------------------

def add_task(description: str, due_date: str | None):
    payload = {
        "description": description,
        "completed": False,
    }

    if due_date:
        payload["due_date"] = due_date  # already ISO

    supabase.table("Tasks").insert(payload).execute()


# -------------------------
# CLEAR COMPLETED
# -------------------------

def clear_tasks():
    supabase.table("Tasks") \
        .delete() \
        .eq("completed", True) \
        .execute()
