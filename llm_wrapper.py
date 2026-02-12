from model import generate_response
from config import SYSTEM_PROMPT, ACTIONS_PROMPT
import json
from datetime import datetime

message_history = []


# ---------------------------
# CHAT FUNCTION
# ---------------------------

def chat(user_input):
    message_history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history
    response = generate_response(messages)
    assistant_response = response.strip()
    message_history.append(
        {"role": "assistant", "content": assistant_response}
    )
    return assistant_response

def parse_actions(query):
    messages = [
        {"role": "system", "content": ACTIONS_PROMPT},
        {"role": "user", "content": query}
    ]
    response = generate_response(messages)
    try:
        data = json.loads(response)
        if "action" not in data:
            return None
        if data["action"] != "add_task":
            return None
        description = data.get("description")
        due_date = data.get("due_date")
        if not description:
            return None
        return {
            "description": description,
            "due_date": due_date
        }
    except json.JSONDecodeError:
        print("Failed to parse JSON:", response)
        return None