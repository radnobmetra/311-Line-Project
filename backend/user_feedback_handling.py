"""
Copy of 311-line-project/user_feedback_handling.py
Needed for remote_chat_frontend.py.
"""

import os
from .session_handling import (
    client,
    PROJECT_ID,
    LOCATION,
    list_events,
)

RUNTIME_NAME = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/"
    f"reasoningEngines/{os.environ['SESSION_AGENT_ENGINE_ID']}"
)


def feedback_type_from_rating(rating: str) -> str:
    """
    Convert a UI rating to Google's feedback type.
    """
    ratings = {
        "up": "THUMBS_UP",
        "down": "THUMBS_DOWN",
    }

    if rating not in ratings:
        raise ValueError("Rating must be 'up' or 'down'.")

    return ratings[rating]


def save_feedback(
    session_id: str,
    event_id: str,
    rating: str,
    user_id: str,
    comment: str = "",
    labels: list[str] | None = None,
):
    """
    Save feedback for a specific agent response.
    """

    if not session_id or not event_id or not user_id:
        raise ValueError("session_id, event_id, and user_id are required.")

    feedback_type = feedback_type_from_rating(rating)

    operation = client.feedback_entries.create(
        name=RUNTIME_NAME,
        session_id=str(session_id),
        event_id=str(event_id),
        feedback_type=feedback_type,
        config={
            "feedback_text": comment,
            "feedback_labels": labels or [],
            "user_id": user_id,
            "source": "311-chat-ui",
        },
    )

    feedback = operation.response

    if feedback is None:
        raise RuntimeError("Feedback creation did not return an entry.")

    return feedback


def get_feedback(feedback_name: str):
    """
    Retrieve a previously saved feedback entry.
    """
    return client.feedback_entries.get(name=feedback_name)


def update_feedback(
    feedback_name: str,
    rating: str,
    comment: str = "",
    labels: list[str] | None = None,
):
    """
    Update an existing feedback entry
    """
    feedback_type = feedback_type_from_rating(rating)

    operation = client.feedback_entries.update(
        name=feedback_name,
        config={
            "feedback_type": feedback_type,
            "feedback_text": comment,
            "feedback_labels": labels or [],
            "update_mask": ("feedbackType,feedbackText,feedbackLabels"),
        },
    )

    if operation.response is None:
        raise RuntimeError("Feedback update did not return a completed entry.")

    return operation.response


def find_response_event_id(
    session_id: str,
    response_event: dict,
    response_text: str,
) -> str:
    """
    Find the saved ADK event ID for the response
    actually displayed to the user.

    Match the author, invocation, and response text.
    Also check the streamed event ID if available.
    """

    author = response_event.get("author")
    invocation_id = response_event.get("invocationId") or response_event.get(
        "invocation_id"
    )
    streamed_id = response_event.get("id")

    if not author or not response_text:
        raise ValueError("No valid agent response to rate.")

    matches = []

    for event in list_events(session_id):
        if event.author != author:
            continue

        if invocation_id and event.invocation_id != invocation_id:
            continue

        raw_event = getattr(event, "raw_event", None) or {}

        if not isinstance(raw_event, dict):
            continue

        event_id = raw_event.get("id")

        if not event_id:
            continue

        if streamed_id and str(event_id) != str(streamed_id):
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        saved_text = next(
            (part.text for part in parts if getattr(part, "text", None)),
            None,
        )

        if saved_text == response_text:
            matches.append(str(event_id))

    if len(matches) != 1:
        raise RuntimeError(
            "Could not uniquely match the displayed "
            "response to a saved ADK event. "
            f"Found {len(matches)} matches. "
            "Feedback was not submitted."
        )

    return matches[0]


def find_existing_feedback(
    session_id: str,
    event_id: str,
    user_id: str,
):
    """
    Find existing feedback in Google Cloud for
    a specific user, session, and response event.
    """

    # Retrieve feedback directly from Google Cloud
    entries = client.feedback_entries.list(parent=RUNTIME_NAME)

    matches = []

    for entry in entries:
        if (
            str(entry.session_id) == str(session_id)
            and str(entry.event_id) == str(event_id)
            and str(entry.user_id) == str(user_id)
        ):
            matches.append(entry)

    if not matches:
        return None

    # If duplicates exist, use the most recently updated
    return max(
        matches, key=lambda entry: str(getattr(entry, "update_time", None) or "")
    )
