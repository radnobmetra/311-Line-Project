import time
import json
import os

#checks if user is still around
HURRY_UP = "useronline.json"

#logs messages and resets timer
def update_user_status(user_id: str, new_message: str):
    sessions = {}
    if os.path.exists(HURRY_UP):
        with open(HURRY_UP, "r") as file:
            try:
                sessions = json.load(file)
            except json.JSONDecodeError:
                pass

    if user_id not in sessions:
        sessions[user_id] = {"transcript": "", "last_active": 0}

    sessions[user_id]["transcript"] += f"User: {new_message}\n"
    sessions[user_id]["last_active"] = time.time()
    with open(HURRY_UP, "w") as file:
        json.dump(sessions, file, indent=4)