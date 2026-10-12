"""
this tests:
deployed AdkApp -> managed session -> message -> second message, same Session ID -> saved events -> reopen -> delete
"""
import asyncio
import os
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
import agentplatform


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
RUNTIME_FILE = PROJECT_ROOT / "runtime_id.txt"

load_dotenv(ENV_FILE)


PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
RUNTIME_LOCATION = os.environ.get(
    "AGENT_RUNTIME_LOCATION",
    "us",
)

TICKET_NUMBER = "260507-3736003"

# Credentials
credential_path = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS"
)

if credential_path:
    credential_path = Path(credential_path)

    if not credential_path.is_absolute():
        credential_path = (
            PROJECT_ROOT / credential_path
        ).resolve()

    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"
    ] = str(credential_path)

# Helpers
@pytest.fixture(scope="session")
def remote_agent():
    assert RUNTIME_FILE.is_file(), (
        "runtime_id.txt does not exist. "
        "Deploy the runtime before running remote tests."
    )

    runtime_name = RUNTIME_FILE.read_text(
        encoding="utf-8"
    ).strip()

    assert runtime_name, "runtime_id.txt is empty"

    client = agentplatform.Client(
        project=PROJECT_ID,
        location=RUNTIME_LOCATION,
    )

    # Support both Agent Platform SDK layouts.
    if (
        hasattr(client, "runtimes")
        and hasattr(client.runtimes, "get")
    ):
        runtimes_api = client.runtimes
    else:
        runtimes_api = client.agent_engines

    return runtimes_api.get(
        name=runtime_name
    )


async def _collect_remote_events(
    remote_agent,
    message: str,
):
    user_id = (
        "story1-pytest-"
        + uuid4().hex[:10]
    )

    session = await remote_agent.async_create_session(
        user_id=user_id
    )

    if isinstance(session, dict):
        session_id = session.get("id")
    else:
        session_id = session.id

    assert session_id, (
        f"Runtime did not return a session ID: {session}"
    )

    events = []

    async for event in remote_agent.async_stream_query(
        user_id=user_id,
        session_id=session_id,
        message=message,
    ):
        events.append(event)

    return events


def run_remote_query(
    remote_agent,
    message: str,
):
    # Prevent a broken runtime from hanging pytest forever
    return asyncio.run(
        asyncio.wait_for(
            _collect_remote_events(
                remote_agent,
                message,
            ),
            timeout=180,
        )
    )


def get_authors(events):
    return {
        event.get("author")
        for event in events
        if isinstance(event, dict)
    }


def get_function_calls(events, name=None):
    calls = []

    for event in events:
        content = event.get("content") or {}

        for part in content.get("parts", []):
            call = part.get("function_call")

            if not call:
                continue

            if name is None or call.get("name") == name:
                calls.append(call)

    return calls


def get_function_responses(events, name=None):
    responses = []

    for event in events:
        content = event.get("content") or {}

        for part in content.get("parts", []):
            response = part.get("function_response")

            if not response:
                continue

            if (
                name is None
                or response.get("name") == name
            ):
                responses.append(response)

    return responses


def get_state_values(events, key):
    values = []

    for event in events:
        actions = event.get("actions") or {}
        state = actions.get("state_delta") or {}

        if key in state:
            values.append(state[key])

    return values


#Task 3
@pytest.mark.remote
def test_remote_qa_routes_through_overseer_and_uses_search_tool(
    remote_agent,
):
    events = run_remote_query(
        remote_agent,
        (
            "How do I report a missed garbage pickup "
            "in the City of Sacramento?"
        ),
    )

    authors = get_authors(events)

    # Request reached the real deployed overseer
    assert "OverseerAgent" in authors

    # Overseer used the Q&A workflow
    assert get_function_calls(
        events,
        "QAWorkflowAgent",
    ), "Overseer never invoked QAWorkflowAgent"

    # Q&A agent used its external knowledge tool
    assert get_function_calls(
        events,
        "search_knowledge_tool",
    ), "Q&A agent never called search_knowledge_tool"

    responses = get_function_responses(
        events,
        "search_knowledge_tool",
    )

    assert responses, (
        "search_knowledge_tool was called but no "
        "tool response was returned"
    )

    result = (
        responses[0]
        .get("response", {})
        .get("result")
    )

    assert isinstance(result, list)
    assert result, (
        "Knowledge search returned no documents"
    )

    # Make sure these are actually City knowledge results, not empty/tool response
    assert any(
        "Sacramento" in doc.get("source", "")
        or "cityofsacramento" in doc.get("url", "")
        for doc in result
    ), "Knowledge search returned no Sacramento source"

    reviews = get_state_values(
        events,
        "qa_review",
    )

    assert "pass" in reviews, (
        f"QA reviewer did not pass the answer: {reviews}"
    )


@pytest.mark.remote
def test_remote_ticket_status_routes_and_calls_arcgis_tool(
    remote_agent,
):
    events = run_remote_query(
        remote_agent,
        (
            "What is the status of ticket "
            f"{TICKET_NUMBER}?"
        ),
    )

    authors = get_authors(events)

    # Must start at overseer
    assert "OverseerAgent" in authors

    # Must reach 2nd specialist workflow
    assert "TicketStatusWorkflowAgent" in authors
    assert "TicketStatusAgent" in authors

    calls = get_function_calls(
        events,
        "get_ticket_details",
    )

    assert calls, (
        "TicketStatusAgent never called "
        "get_ticket_details"
    )

    called_number = (
        calls[0]
        .get("args", {})
        .get("ticket_number", "")
    )

    assert called_number.replace("-", "") == (
        TICKET_NUMBER.replace("-", "")
    )

    responses = get_function_responses(
        events,
        "get_ticket_details",
    )

    assert responses, (
        "get_ticket_details did not return "
        "a tool response"
    )

    ticket = responses[0].get(
        "response",
        {},
    )

    assert ticket.get(
        "Reference number"
    ) == TICKET_NUMBER

    assert ticket.get(
        "Case Status"
    ), "ArcGIS ticket response had no case status"

    # Verify the tool result actually became an agent answer
    ticket_answers = get_state_values(
        events,
        "ticketstatus",
    )

    assert ticket_answers, (
        "Ticket status workflow did not produce "
        "a ticket answer"
    )

    assert TICKET_NUMBER in ticket_answers[-1]


@pytest.mark.remote
def test_remote_managed_session_creation(remote_agent):
    async def create():
        user_id = (
            "managed-runtime-test-"
            + uuid4().hex[:8]
        )

        session = await remote_agent.async_create_session(
            user_id=user_id
        )

        return user_id, session

    user_id, session = asyncio.run(create())

    print()
    print("User:", user_id)
    print("Session:", session)

    assert session

    if isinstance(session, dict):
        assert session.get("id")
    else:
        assert session.id

@pytest.mark.remote
def test_remote_managed_session_persists_multiple_turns(
    remote_agent,
):
    async def run():
        user_id = (
            "managed-multiturn-test-"
            + uuid4().hex[:8]
        )

        session = await remote_agent.async_create_session(
            user_id=user_id
        )

        session_id = (
            session["id"]
            if isinstance(session, dict)
            else session.id
        )

        try:
            print()
            print("User:", user_id)
            print("Session ID:", session_id)

            # TURN 1
            turn_1_events = []

            async for event in remote_agent.async_stream_query(
                user_id=user_id,
                session_id=session_id,
                message=(
                    "How do I report a missed garbage pickup "
                    "in the City of Sacramento?"
                ),
            ):
                turn_1_events.append(event)

            assert turn_1_events

            # TURN 2 - SAME SESSION
            turn_2_events = []

            async for event in remote_agent.async_stream_query(
                user_id=user_id,
                session_id=session_id,
                message="Do I have to pay a fee for that?",
            ):
                turn_2_events.append(event)

            assert turn_2_events

            # REOPEN
            reopened = await remote_agent.async_get_session(
                user_id=user_id,
                session_id=session_id,
            )

            if isinstance(reopened, dict):
                reopened_id = reopened.get("id")
                events = reopened.get("events", [])
            else:
                reopened_id = reopened.id
                events = reopened.events

            assert reopened_id == session_id
            assert events

            print("Reopened session:", reopened_id)
            print("Persisted event count:", len(events))

        finally:
            await remote_agent.async_delete_session(
                user_id=user_id,
                session_id=session_id,
            )

            print("Deleted session:", session_id)

    asyncio.run(run())