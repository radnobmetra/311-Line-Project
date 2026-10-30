
import asyncio
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

from session_handling import (
    client,
    create_update_agent_session,
    list_events,
)
from user_feedback_handling import (
    find_response_event_id,
    find_existing_feedback,
    feedback_type_from_rating,
    save_feedback,
    get_feedback,
    update_feedback,
)
from evaluation_handling import evaluate_completed_session


RUNTIME_FILE = PROJECT_ROOT / "runtime_id.txt"


def get_remote_agent():
    """
    Retrieve the deployed agent using the client
    already initialized in session_handling.py.
    """
    runtime_name = RUNTIME_FILE.read_text(
        encoding="utf-8"
    ).strip()

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



async def main():
    remote_agent = get_remote_agent()

    user_number = "eval-test-3e3832339a"
    source = "terminal"
    user_id = f"{user_number}-{source}"

    # Setup Initial Session state variables to avoid reference errors before the loop
    session_id = None
    last_response_event = None
    last_response_text = None
    debug = False

    print()
    print("Connected to deployed 311 Agent Runtime")
    print("User:", user_id)
    print("Commands:")
    print("  /session       show current session ID")
    print("  /events        show saved session events")
    print("  /evaluate      evaluate the current session")
    print("  /debug         toggle agent/tool tracing")
    print("  /up            rate last response helpful")
    print("  /down          rate last response not helpful")
    print("  /feedback      retrieve current response feedback")
    print("  /quit          exit")
    print()
    print("You can also enter /up or /down followed by a comment.")
    print()

    while True:
        message = input("You: ").strip()

        if not message:
            continue

        if message == "/quit":
            break

        # time over handling
        new_session_id = create_update_agent_session(
            user_Number=user_number,
            ttl=1000,  # timer
            source=source,
        )
        
        # if session rolled over due to a time over, resets the last response context so you don't rate an old session's event
        if session_id != new_session_id:
            if session_id is not None:
                print(f"\n[SYSTEM: TTL Expired. Session {session_id} marked as resolved.]")
            session_id = new_session_id
            last_response_event, last_response_text = restore_last_response(session_id)
            
        if message == "/session":
            print("Session:", session_id)
            continue

        if message == "/debug":
            debug = not debug
            print("Debug tracing:", "ON" if debug else "OFF")
            continue

        if message == "/events":
            try:
                events = list_events(session_id)

                print(f"\nSaved events: {len(events)}")

                for event in events:
                    print(
                        f"  {event.author} | "
                        f"{event.invocation_id}"
                    )

            except Exception as error:
                print("Could not retrieve events:", error)

            print()
            continue

        if message == "/evaluate":
            print("\nEvaluating session...")
            print("This may take a while.\n")

            try:
                result = await asyncio.to_thread(
                    evaluate_completed_session,
                    session_id,
                )

                if result is None:
                    print(
                        "Evaluation returned no result. "
                        "Check the error output from the evaluation module."
                    )
                else:
                    print("\n=== SESSION EVALUATION ===")
                    print("Session:", result["session_id"])
                    print("Metric:", result["metric_version"])
                    print("Score:", result["score"])

                    print("\nRubric verdicts:")
                    from pprint import pprint
                    pprint(result["rubric_verdicts"])

                    print("==========================\n")

            except Exception as error:
                print("Evaluation failed:", error)
            continue

        # FEEDBACK COMMANDS
        command, _, comment = message.partition(" ")

        if command in ("/up", "/down"):
            if last_response_event is None:
                print("No agent response available to rate.")
                continue

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
                        raise RuntimeError(
                            "Existing feedback targets a "
                            "different response."
                        )

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
                    raise RuntimeError(
                        "Google did not return a feedback name."
                    )

                # Read the feedback back from Google.
                verified = get_feedback(feedback.name)

                if (
                    str(verified.session_id) != str(session_id)
                    or str(verified.event_id) != str(event_id)
                    or verified.feedback_type
                    != feedback_type_from_rating(rating)
                ):
                    raise RuntimeError(
                        "Saved feedback did not match "
                        "the requested response and rating."
                    )

                print()
                print("Feedback saved and verified!")
                print("Rating:", verified.feedback_type)
                print("Session:", verified.session_id)
                print("Event:", verified.event_id)
                print("Feedback name:", verified.name)
                print()

            except Exception as error:
                print(
                    "Feedback operation or verification "
                    f"failed: {error}"
                )
                print("You can retry. The chat is unaffected.")

            continue

        if message == "/feedback":
            if last_response_event is None:
                print("No agent response available.")
                continue

            try:
                event_id = find_response_event_id(
                    session_id,
                    last_response_event,
                    last_response_text,
                )

                existing = find_existing_feedback(
                    session_id=session_id,
                    event_id=event_id,
                    user_id=user_id,
                )

                if existing is None:
                    print("No saved feedback for this response.")
                    continue

                feedback = get_feedback(existing.name)

                if (
                    str(feedback.session_id) != str(session_id)
                    or str(feedback.event_id) != str(event_id)
                ):
                    raise RuntimeError(
                        "Retrieved feedback does not match "
                        "the current response."
                    )

                print()
                print("Saved feedback:")
                print("Rating:", feedback.feedback_type)
                print("Comment:", feedback.feedback_text or "[No comment]")
                print("Session:", feedback.session_id)
                print("Event:", feedback.event_id)
                print("Feedback name:", feedback.name)
                print()

            except Exception as error:
                print("Could not retrieve feedback:", error)

            continue

        # AGENT CHAT
        final_text = None
        final_event = None

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

            # Prefer the user-visible Overseer response.
            if event.get("author") == "OverseerAgent":
                final_text = text
                final_event = event

            # Fallback if no Overseer answer is available.
            elif final_text is None:
                final_text = text
                final_event = event

        print()
        print(
            "Agent:",
            final_text or "[No text response returned]"
        )
        print()

        # Remember the exact event selected for display.
        last_response_event = final_event
        last_response_text = final_text

        if final_event is not None:
            print("Rate this response with /up or /down.")
            print()


if __name__ == "__main__":
    asyncio.run(main())

