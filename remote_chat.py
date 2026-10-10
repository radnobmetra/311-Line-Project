import asyncio
import os
from pathlib import Path
from uuid import uuid4

import agentplatform
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get(
    "AGENT_RUNTIME_LOCATION",
    "us",
)

RUNTIME_FILE = PROJECT_ROOT / "runtime_id.txt"


def get_client_and_remote_agent():
    runtime_name = RUNTIME_FILE.read_text(
        encoding="utf-8"
    ).strip()

    client = agentplatform.Client(
        project=PROJECT_ID,
        location=LOCATION,
    )

    if (
        hasattr(client, "runtimes")
        and hasattr(client.runtimes, "get")
    ):
        remote_agent = client.runtimes.get(
            name=runtime_name
        )
    else:
        remote_agent = client.agent_engines.get(
            name=runtime_name
        )

    return client, remote_agent

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
    if not isinstance(event, dict):
        return

    author = event.get("author")
    branch = event.get("branch")
    invocation_id = _first(
        event,
        "invocationId",
        "invocation_id",
    )

    content = event.get("content") or {}
    parts = content.get("parts") or []

    # AGENT / EVENT HEADER
    if author:
        print(f"\n  [{author}]")

    if branch:
        print(f"    branch: {branch}")

    if invocation_id:
        print(f"    invocation: {invocation_id}")

    # CONTENT
    for part in parts:
        if not isinstance(part, dict):
            continue

        # Support both camelCase and snake_case because SDK serialization can differ
        function_call = _first(
            part,
            "functionCall",
            "function_call",
        )

        function_response = _first(
            part,
            "functionResponse",
            "function_response",
        )

        tool_call = _first(
            part,
            "toolCall",
            "tool_call",
        )

        tool_response = _first(
            part,
            "toolResponse",
            "tool_response",
        )

        text = part.get("text")

        if function_call:
            name = function_call.get("name")
            args = function_call.get("args")

            print(f"    CALL: {name}")
            print(f"      args: {_short(args)}")

        if function_response:
            name = function_response.get("name")
            response = function_response.get("response")

            print(f"    RESPONSE: {name}")
            print(
                f"      result: {_short(response)}"
            )

        if tool_call:
            print(
                "    TOOL CALL:",
                _short(tool_call),
            )

        if tool_response:
            print(
                "    TOOL RESPONSE:",
                _short(tool_response),
            )

        if text:
            print(
                "    text:",
                _short(text),
            )

    # STATE CHANGES
    actions = event.get("actions") or {}

    state_delta = _first(
        actions,
        "stateDelta",
        "state_delta",
    )

    if state_delta:
        print("    STATE:")

        for key, value in state_delta.items():
            print(
                f"      {key}: {_short(value)}"
            )

    # AGENT TRANSFER
    transfer = _first(
        actions,
        "transferToAgent",
        "transfer_to_agent",
    )

    if transfer:
        print(
            f"    TRANSFER -> {transfer}"
        )

async def main():
    client, remote_agent = get_client_and_remote_agent()

    user_id = (
        "remote-chat-"
        + uuid4().hex[:8]
    )

    session = await remote_agent.async_create_session(
        user_id=user_id
    )

    if isinstance(session, dict):
        session_id = session["id"]
    else:
        session_id = session.id

    debug = False
    print()
    print("Connected to deployed 311 Agent Runtime")
    print("User:", user_id)
    print("Session:", session_id)
    print()
    print("Commands:")
    print("  /session   show current session ID")
    print("  /debug     toggle agent/tool tracing")
    print("  /quit      exit")
    print()

    while True:
        message = input("You: ").strip()

        if not message:
            continue

        if message == "/quit":
            break

        if message == "/session":
            print("Session:", session_id)
            continue
        if message == "/debug":
            debug = not debug
            print(
                "Debug tracing:",
                "ON" if debug else "OFF",
            )
            continue

        final_text = None

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

            # Prefer the final response produced by your Overseer.
            if event.get("author") == "OverseerAgent":
                final_text = text

            # Fallback in case another execution path returns text.
            elif final_text is None:
                final_text = text

        print()
        print(
            "Agent:",
            final_text or "[No text response returned]",
        )
        print()


if __name__ == "__main__":
    asyncio.run(main())