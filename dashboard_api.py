import os
import json
import time

from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request

import session_handling

app = Flask(__name__)

# Cache settings, in seconds.
SESSION_CACHE_SECONDS = 60
OUTCOME_CACHE_SECONDS = 120

session_cache = {
    "expires": 0,
    "sessions": []
}
session_cache_lock = Lock()

outcome_cache = {}
outcome_cache_lock = Lock()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Cache-Control"] = "no-store"
    return response


def format_timestamp(value):
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def phone_from_user_id(user_id):
    if user_id.endswith("-sms"):
        return user_id[:-4]
    return user_id


def get_google_sessions():
    """
    Cache the Google session list for 60 seconds.
    Avoid repeatedly requesting the same list.
    """
    with session_cache_lock:
        if time.monotonic() >= session_cache["expires"]:
            session_cache["sessions"] = session_handling.list_sessions()
            session_cache["expires"] = (
                time.monotonic() + SESSION_CACHE_SECONDS
            )

        return list(session_cache["sessions"])


def format_session(session, include_events=False):
    """
    Return lightweight metadata by default.
    Retrieve full event history only when requested.
    """
    session_id = session.name.rsplit("/", 1)[-1]
    user_id = session.user_id or "unknown"

    result = {
        "id": session_id,
        "contactId": user_id,
        "status": "Stored",
        "startedAt": format_timestamp(session.create_time),
        "lastMessageAt": format_timestamp(session.update_time)
    }

    if include_events:
        events = session_handling.list_events(session_id)

        result["events"] = []

        for event in events:
            content = getattr(event, "content", None)
            parts = getattr(content, "parts", None) or []

            result["events"].append({
                "author": event.author,
                "timestamp": format_timestamp(getattr(event, "timestamp", None)),
                "content": {
                    "parts": [
                        {"text": getattr(part, "text", None) or ""}
                        for part in parts
                    ]
                }
            })

    return result


def get_session_outcome(session):
    """
    Retrieve a session's saved final_outcome.
    Use a cache to avoid repeatedly downloading
    the same event history.
    """
    session_id = session.name.rsplit("/", 1)[-1]
    update_time = format_timestamp(session.update_time)
    now = time.monotonic()

    with outcome_cache_lock:
        cached = outcome_cache.get(session_id)

        if (
            cached is not None
            and cached["update_time"] == update_time
            and now - cached["fetched_at"] < OUTCOME_CACHE_SECONDS
        ):
            return session_id, cached["outcome"]

    events = session_handling.list_events(session_id)
    outcome = None

    # Events are returned in chronological order.
    # Keep the most recent valid final outcome.
    for event in events:
        if event.author != "system":
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        for part in parts:
            text = getattr(part, "text", None)

            if not text or "final_outcome" not in text:
                continue

            try:
                data = json.loads(text)

                if isinstance(data, dict):
                    value = data.get("final_outcome")

                    if isinstance(value, str):
                        value = value.strip().upper()

                        if value in ("HELPED", "NOT_HELPED", "UNCLEAR"):
                            outcome = value

            except (json.JSONDecodeError, TypeError):
                continue

    with outcome_cache_lock:
        outcome_cache[session_id] = {
            "outcome": outcome,
            "update_time": update_time,
            "fetched_at": time.monotonic()
        }

    return session_id, outcome



# Get session metadata without downloading event histories.
@app.get("/sessions")
def get_sessions():
    google_sessions = get_google_sessions()

    contact_id = request.args.get("contactId")

    if contact_id:
        google_sessions = [
            session for session in google_sessions
            if session.user_id == contact_id
        ]

    sessions = [
        format_session(session)
        for session in google_sessions
    ]

    return jsonify(sessions)



# SLOWER: Load outcomes separately, using cached values.
@app.get("/sessions/outcomes")
def get_outcomes():
    google_sessions = get_google_sessions()

    contact_id = request.args.get("contactId")

    if contact_id:
        google_sessions = [
            session for session in google_sessions
            if session.user_id == contact_id
        ]

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(
            get_session_outcome,
            google_sessions
        ))

    return jsonify(dict(results))


# Get one session with its full event history.
@app.get("/sessions/<session_id>")
def get_session(session_id):
    session_name = (
        f"projects/{session_handling.PROJECT_ID}"
        f"/locations/{session_handling.LOCATION}"
        f"/reasoningEngines/{os.environ['SESSION_AGENT_ENGINE_ID']}"
        f"/sessions/{session_id}"
    )

    session = session_handling.client.sessions.get(
        name=session_name
    )

    return jsonify(
        format_session(session, include_events=True)
    )


@app.get("/contacts/<path:user_id>")
def get_contact(user_id):
    return jsonify({
        "id": user_id,
        "phoneNumber": phone_from_user_id(user_id),
        "createdAt": ""
    })


@app.get("/contacts")
def get_contacts():
    contacts = {}

    for session in get_google_sessions():
        user_id = session.user_id or "unknown"

        if user_id not in contacts:
            contacts[user_id] = {
                "id": user_id,
                "phoneNumber": phone_from_user_id(user_id),
                "createdAt": format_timestamp(session.create_time)
            }

    return jsonify(list(contacts.values()))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
