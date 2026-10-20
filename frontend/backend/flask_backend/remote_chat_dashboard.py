"""
This file is a copy of remote_chat.py that has been modified for integration
with the frontend.
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv
import json
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

load_dotenv(PROJECT_ROOT / ".env")

from .session_handling import (
    client,
    create_update_agent_session,
    list_events,
)
from .user_feedback_handling import (
    find_response_event_id,
    find_existing_feedback,
    feedback_type_from_rating,
    save_feedback,
    get_feedback,
    update_feedback,
)
from .evaluation_handling import evaluate_completed_session


runtime_name = os.environ["REASONING_ENGINE_APP_NAME"]

"""
===========================================
            functions 
===========================================
"""

def get_remote_agent():
    """
    Retrieve the deployed agent using the client
    already initialized in session_handling.py.
    """
    #runtime_name = RUNTIME_FILE.read_text(
    #    encoding="utf-8"
    #).strip()

    return client.runtimes.get(name=runtime_name)


def get_text(event):
    if not isinstance(event, dict):
        return None

    content = event.get("content") or {}

    for part in content.get("parts", []):
        text = part.get("text")

        if text:
            return text

    return None

def _first(mapping, *names):
    """Return the first matching key from a dict."""
    if not isinstance(mapping, dict):
        return None

    for name in names:
        if name in mapping:
            return mapping[name]

    return None


def _short(value, limit=600):
    """
    Prevent huge Elasticsearch / ArcGIS responses
    from flooding the terminal.
    """
    text = str(value)

    if len(text) > limit:
        return text[:limit] + "... [truncated]"

    return text


def print_event_trace(event):
    """
    Print a compact trace of agent execution.

    Shows tool calls, responses, reviewer results,
    and agent transfers.
    """
    if not isinstance(event, dict):
        return

    author = event.get("author", "Unknown")
    content = event.get("content") or {}
    parts = content.get("parts") or []

    for part in parts:
        if not isinstance(part, dict):
            continue

        function_call = _first(
            part, "functionCall", "function_call",
            "toolCall", "tool_call"
        )

        function_response = _first(
            part, "functionResponse", "function_response",
            "toolResponse", "tool_response"
        )

        text = part.get("text")

        # Tool or agent call
        if function_call:
            if isinstance(function_call, dict):
                name = function_call.get("name", "unknown")
                args = function_call.get("args")

                print(f"  [{author}] CALL: {name}")

                if args:
                    print(f"    Args: {_short(args, 200)}")
            else:
                print(f"  [{author}] CALL: {_short(function_call, 200)}")

        # Tool or agent response
        elif function_response:
            if isinstance(function_response, dict):
                name = function_response.get("name", "unknown")
                result = function_response.get("response")

                if name == "validateInput":
                    print(
                        f"  [{author}] RESPONSE: {name}"
                        f" -> {_short(result, 100)}"
                    )
                elif isinstance(result, dict) and (
                    "error" in result or "exception" in result
                ):
                    print(
                        f"  [{author}] RESPONSE: {name}"
                        f" -> {_short(result, 200)}"
                    )
                else:
                    print(
                        f"  [{author}] RESPONSE: {name}"
                        " (details hidden)"
                    )
            else:
                print(
                    f"  [{author}] RESPONSE:"
                    f" {_short(function_response, 200)}"
                )

        # Reviewer results are useful, unlike
        # repeated intermediate answer text.
        elif text and author == "QAReviewerAgent":
            print(f"  [{author}] REVIEW: {_short(text, 100)}")

    # Agent transfers
    actions = event.get("actions") or {}

    transfer = _first(
        actions,
        "transferToAgent",
        "transfer_to_agent"
    )

    if transfer:
        print(f"  [{author}] TRANSFER -> {transfer}")



def restore_last_response(session_id):
    """
    Restore the response from the most recent
    user request using the same selection logic
    as the live chat.
    """
    events = list_events(session_id)

    # Find the most recent user request.
    last_user_event = next(
        (
            event for event in reversed(events)
            if event.author == "user"
        ),
        None,
    )

    if last_user_event is None:
        return None, None

    invocation_id = last_user_event.invocation_id

    first_response = None
    overseer_response = None

    for event in events:
        # Only consider events from the last request.
        if (
            event.invocation_id != invocation_id
            or event.author == "user"
        ):
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        text = next(
            (
                part.text
                for part in parts
                if getattr(part, "text", None)
            ),
            None,
        )

        raw_event = getattr(event, "raw_event", None)

        if not (
            text
            and isinstance(raw_event, dict)
            and raw_event.get("id")
        ):
            continue

        response = (
            {
                "author": event.author,
                "invocationId": event.invocation_id,
                "id": raw_event["id"],
            },
            text,
        )

        # Equivalent to the live chat's fallback.
        if first_response is None:
            first_response = response

        # Prefer the latest Overseer answer.
        if event.author == "OverseerAgent":
            overseer_response = response

    return overseer_response or first_response or (None, None)

"""
======================================================================================
                                    gui chat
======================================================================================
"""
# not used for anything
async def gui_make_session() -> str:
    remote_agent = get_remote_agent()
    user_number = "remote-chat-test"
    source = "terminal"
    user_id = f"{user_number}-{source}"
    
    # Create or reuse a session.
    session_id = create_update_agent_session(
        user_Number=user_number,
        ttl=1800,
        source=source,
    )
    return session_id



async def send_message_get_response(message: str) -> json:

    error_msg = {"author": "error", "contents": "An error occurred. Please try again later."}

    print()
    print("User message: " + message)
    print("initializing variables...")

    #initialize variables
    remote_agent = get_remote_agent()
    user_number = "remote-chat-test"
    source = "terminal"
    user_id = f"{user_number}-{source}"

    # Create or reuse a session.
    print("creating or updating a session...")
    session_id = create_update_agent_session(
        user_Number=user_number,
        ttl=1800,
        source=source,
    )

    session = await remote_agent.async_get_session(
        user_id=user_id,
        session_id=session_id,
    )

    if session is None:
        print("error: could not retrieve session from deployed agent.")
        return(error_msg)

    debug = False

    # ==================== handle feedback ======================

    command, _, comment = message.partition(" ")

    # Most recent user-visible response.
    last_response_event, last_response_text = (
        restore_last_response(session_id)
    )

    if command in ("/up", "/down"):
        print("Trying to save user feedback...")
        if last_response_event is None:
            return({"author": "Agent", "contents": "No agent response was available to rate."})
            
        rating = command[1:]

        try:
            event_id = find_response_event_id(
                session_id,
                last_response_event,
                last_response_text,
            )

            previous = find_existing_feedback(
                session_id=session_id,
                event_id=event_id,
                user_id=user_id,
            )

            if previous:
                # Check that we're updating the right entry.
                if (
                    str(previous.session_id) != str(session_id)
                    or str(previous.event_id) != str(event_id)
                ):
                    print("Existing feedback targets a different response.")
                    return(error_msg)

                if (
                    previous.feedback_type
                    == feedback_type_from_rating(rating)
                    and not comment
                ):
                    feedback = previous
                else:
                    feedback = update_feedback(
                        feedback_name=previous.name,
                        rating=rating,
                        comment=comment,
                    )
            else:
                feedback = save_feedback(
                    session_id=session_id,
                    event_id=event_id,
                    rating=rating,
                    user_id=user_id,
                    comment=comment,
                    )

            if feedback is None or not feedback.name:
                print("Google did not return a feedback name.")
                return(error_msg)

            # Read the feedback back from Google.
            verified = get_feedback(feedback.name)

            if (
                str(verified.session_id) != str(session_id)
                or str(verified.event_id) != str(event_id)
                or verified.feedback_type
                != feedback_type_from_rating(rating)
            ):
                print("Saved feedback did not match the requested response and rating.")
                return(error_msg)

            print("Feedback saved and verified!")
            return({"author":"Agent", "contents":"Feedback saved!"})

        except Exception as error:
            print(
                "Feedback operation or verification "
                f"failed: {error}"
            )
            return(error_msg)

    # ==================== message the agent ====================

    # AGENT CHAT
    final_text = None
    msg_author = "Agent"

    print("Getting agent response...")

    async for event in remote_agent.async_stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        if debug:
            print_event_trace(event)

        text = get_text(event)

        if not text:
            continue

        event_author = event.get("author")

        # Prefer the user-visible Overseer response.
        if event_author == "OverseerAgent":
            final_text = text

        #If the session has ended, inform the user and ignore SessionReviewerAgent's output
        elif event_author == "SessionReviewerAgent":
            final_text = "This session has ended. You may need to wait a few minutes before starting a new conversation."

        # Fallback if no Overseer answer is available.
        elif final_text is None:
            final_text = text

    if not final_text:
        final_text="[No text response returned]"


    print("Agent:", final_text)

    return({"author":msg_author, "contents":final_text})

#==================================================================================

if __name__ == "__main__":
    #asyncio.run(main())
    asyncio.run(send_message_get_response("hi"))
