from pathlib import Path
import asyncio
import os
import json
import time
from werkzeug.utils import secure_filename

from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import firebase_admin
from firebase_admin import auth as firebase_auth

from flask import Flask, abort, g, jsonify, request, send_from_directory
from flask_cors import CORS

from . import session_handling

from .remote_chat_dashboard import (
    gui_make_session,
    send_message_get_response,
    send_image_get_response,
)

app = Flask(__name__, static_folder=None)
CORS(app)

# Cache settings, in seconds.
SESSION_CACHE_SECONDS = 60
OUTCOME_CACHE_SECONDS = 120

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
# Angular build location inside the container.
STATIC_DIR = (Path(__file__).resolve().parent.parent / "static").resolve()
UPLOAD_FOLDER = STATIC_DIR / "temp"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

session_cache = {"expires": 0, "sessions": []}
session_cache_lock = Lock()

outcome_cache = {}
outcome_cache_lock = Lock()

error_msg = {
    "author": "error",
    "contents": "An error occurred. Please try again later.",
}

# firebase_admin.initialize_app(options={"projectId": os.environ["FIREBASE_PROJECT_ID"]})
firebase_admin.initialize_app(options={"projectId": "admin-96a00"})


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def valid_user_number(user_number: str):
    # checks if user number is valid. For now, just checks that the user number
    # contains at least 2 characters
    return len(user_number) >= 2


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
            session_cache["expires"] = time.monotonic() + SESSION_CACHE_SECONDS

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
        "lastMessageAt": format_timestamp(session.update_time),
    }

    if include_events:
        events = session_handling.list_events(session_id)

        result["events"] = []

        for event in events:
            content = getattr(event, "content", None)
            parts = getattr(content, "parts", None) or []

            result["events"].append(
                {
                    "author": event.author,
                    "timestamp": format_timestamp(getattr(event, "timestamp", None)),
                    "content": {
                        "parts": [
                            {"text": getattr(part, "text", None) or ""}
                            for part in parts
                        ]
                    },
                }
            )

    return result


def get_session_evaluation(session):
    """
    Retrieve a session's saved evaluation results,
    including the AI score, feedback, and final outcome.
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
            return session_id, cached["evaluation"]

    events = session_handling.list_events(session_id)
    evaluation = None

    # Process events chronologically.
    ordered_events = sorted(
        events, key=lambda event: format_timestamp(getattr(event, "timestamp", None))
    )

    for event in ordered_events:
        if event.author not in ("system", "eval_author"):
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        for part in parts:
            text = getattr(part, "text", None)

            if not isinstance(text, str) or "final_outcome" not in text:
                continue

            try:
                data = json.loads(text)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            outcome = data.get("final_outcome")

            if not isinstance(outcome, str):
                continue

            outcome = outcome.strip().upper()

            if outcome not in ("HELPED", "NOT_HELPED", "UNCLEAR"):
                continue

            evaluation = {
                "ai_evaluation": (
                    data.get("ai_evaluation")
                    if isinstance(data.get("ai_evaluation"), dict)
                    else None
                ),
                "user_feedback": (
                    data.get("user_feedback")
                    if isinstance(data.get("user_feedback"), dict)
                    else None
                ),
                "final_outcome": outcome,
            }

    with outcome_cache_lock:
        outcome_cache[session_id] = {
            "evaluation": evaluation,
            "update_time": update_time,
            "fetched_at": time.monotonic(),
        }

    return session_id, evaluation


@app.route("/api/sendMessage", methods=["POST"])
def sendMessage():
    userNumber = str(request.json.get("userNumber"))
    userMessage = str(request.json.get("message"))
    if not (userNumber and userMessage):
        return error_msg
    responseJson = asyncio.run(send_message_get_response(userNumber, userMessage))
    return responseJson


@app.route("/api/sendImage", methods=["POST"])
def sendImage():
    # return error message for requests without a user id
    if "userNumber" not in request.form:
        return error_msg

    # get user number
    user_number = request.form["userNumber"]
    if valid_user_number(user_number) is False:
        return error_msg

    # get file
    if "userUpload" not in request.files:
        return error_msg
    file = request.files["userUpload"]
    if file.filename == "":
        return error_msg

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        # send image to agent
        responseJson = asyncio.run(send_image_get_response(filepath, user_number))
        return responseJson

    return error_msg


# Return current logged in user's email. Information is returned from auth interceptor
@app.get("/api/user")
def get_current_user():
    return jsonify(
        {
            "id": g.user["uid"],
            "name": "Admin",
            "username": g.user.get("email"),
            "email": g.user.get("email"),
        }
    )


# Get session metadata without downloading event histories.
@app.get("/api/sessions")
def get_sessions():
    google_sessions = get_google_sessions()

    contact_id = request.args.get("contactId")

    if contact_id:
        google_sessions = [
            session for session in google_sessions if session.user_id == contact_id
        ]

    sessions = [format_session(session) for session in google_sessions]

    return jsonify(sessions)


# SLOWER: Load outcomes separately, using cached values.
@app.get("/api/sessions/outcomes")
def get_outcomes():
    google_sessions = get_google_sessions()

    contact_id = request.args.get("contactId")

    if contact_id:
        google_sessions = [
            session for session in google_sessions if session.user_id == contact_id
        ]

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(get_session_evaluation, google_sessions))

    return jsonify(
        {
            session_id: (evaluation["final_outcome"] if evaluation else None)
            for session_id, evaluation in results
        }
    )


@app.get("/api/sessions/evaluations")
def get_evaluations():
    """
    Return individual AI evaluations, user feedback,
    and combined final outcomes for all sessions.
    """
    google_sessions = get_google_sessions()

    contact_id = request.args.get("contactId")

    if contact_id:
        google_sessions = [
            session for session in google_sessions if session.user_id == contact_id
        ]

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(get_session_evaluation, google_sessions))

    return jsonify(dict(results))


# Get one session with its full event history.
@app.get("/api/sessions/<session_id>")
def get_session(session_id):
    session_name = (
        f"projects/{session_handling.PROJECT_ID}"
        f"/locations/{session_handling.LOCATION}"
        f"/reasoningEngines/{os.environ['SESSION_AGENT_ENGINE_ID']}"
        f"/sessions/{session_id}"
    )

    session = session_handling.client.sessions.get(name=session_name)

    return jsonify(format_session(session, include_events=True))


@app.get("/api/contacts/<path:user_id>")
def get_contact(user_id):
    return jsonify(
        {"id": user_id, "phoneNumber": phone_from_user_id(user_id), "createdAt": ""}
    )


@app.get("/api/contacts")
def get_contacts():
    contacts = {}

    for session in get_google_sessions():
        user_id = session.user_id or "unknown"

        if user_id not in contacts:
            contacts[user_id] = {
                "id": user_id,
                "phoneNumber": phone_from_user_id(user_id),
                "createdAt": format_timestamp(session.create_time),
            }

    return jsonify(list(contacts.values()))


# Return a JSON status indicating that the backend is running.
@app.get("/api/test")
def test():
    return jsonify({"status": "ok"})


# After the dashboard is built in the container, this API function serves the built frontend website.
@app.get("/", defaults={"path": ""})
@app.get("/<path:path>")
def serve_frontend(path):
    # Unknown API endpoints must not return Angular HTML.
    if path == "api" or path.startswith("api/"):
        return jsonify({"error": "Endpoint not found"}), 404

    requested_file = (STATIC_DIR / path).resolve()

    # Prevent access outside the Angular build directory.
    if not requested_file.is_relative_to(STATIC_DIR):
        abort(404)

    if requested_file.is_file():
        return send_from_directory(STATIC_DIR, path)

    # Return 404 for missing assets.
    if Path(path).suffix:
        abort(404)

    # Let Angular handle frontend routes.
    response = send_from_directory(STATIC_DIR, "index.html")
    response.headers["Cache-Control"] = "no-cache"
    return response


# This function gets called before every API request to make sure it's protected.
# Secured backend API endpoints by verifying Firebase tokens with the Firebase Admin SDK.
# Reject missing or invalid tokens with `401`.
# @app.before_request
def protect_api():
    path = request.path

    # Angular pages and assets can load without a token.
    if path != "/api" and not path.startswith("/api/"):
        return None

    # Public test check.
    if path == "/api/test":
        return None

    authorization = request.headers.get("Authorization", "")
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Authentication required"}), 401

    token = parts[1]

    try:
        decoded_token = firebase_auth.verify_id_token(token)

    except firebase_auth.CertificateFetchError:
        # Verification service failure; still deny access.
        return jsonify({"error": "Authentication temporarily unavailable"}), 503

    except (firebase_auth.InvalidIdTokenError, ValueError):
        return jsonify({"error": "Invalid or expired token"}), 401

    # Make verified identity available to this request's routes.
    g.user = decoded_token
