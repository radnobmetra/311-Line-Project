"""
this specifically tests:
Agent Platform API reachable -> correct Runtime selected -> CREATE session -> GET same session -> LIST contains session -> DELETE session
It doesn't send messages through the deployed 311 agent. For end-to-end tests of the deployed agent, including multi-turn session persistence, see test_remote_runtime.py.
"""

import os
from pathlib import Path
from uuid import uuid4

import agentplatform
import pytest
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]

LOCATION = os.environ.get(
    "AGENT_RUNTIME_LOCATION",
    "us",
)

EXPECTED_ENGINE_ID = os.environ[
    "SESSION_AGENT_ENGINE_ID"
]

RUNTIME_FILE = PROJECT_ROOT / "runtime_id.txt"


def _runtime_name() -> str:
    assert RUNTIME_FILE.is_file(), (
        "runtime_id.txt does not exist"
    )

    name = RUNTIME_FILE.read_text(
        encoding="utf-8"
    ).strip()

    assert name, "runtime_id.txt is empty"

    # Make sure this test is pointed at the same Agent Runtime configured for the deployed application
    actual_engine_id = name.rsplit("/", 1)[-1]

    assert actual_engine_id == EXPECTED_ENGINE_ID, (
        "Agent Runtime mismatch.\n"
        f"runtime_id.txt: {actual_engine_id}\n"
        f".env:           {EXPECTED_ENGINE_ID}"
    )

    return name


@pytest.mark.remote
def test_agent_platform_managed_session_lifecycle():
    client = agentplatform.Client(
        project=PROJECT_ID,
        location=LOCATION,
    )

    runtime_name = _runtime_name()

    sessions_api = (
        client.agent_engines.sessions
    )

    user_id = (
        "managed-session-preflight-"
        + uuid4().hex[:8]
    )

    session = None

    try:
        # CREATE
        created = sessions_api.create(
            name=runtime_name,
            user_id=user_id,
            config={
                # Agent Platform requires a minimum 24-hour TTL.
                "ttl": "86400s",
                "wait_for_completion": True,
            },
        )

        # create() may return either the Session resource itself, or an operation containing the Session in .response
        session = (
            getattr(
                created,
                "response",
                None,
            )
            or created
        )

        print()
        print("Created:", session.name)

        assert session.name
        assert "/sessions/" in session.name

        # Ensure the operation was actually completed/unwrapped
        assert "/operations/" not in session.name, (
            "Session create returned an operation instead "
            "of the completed Session resource"
        )

        # Make sure the session belongs to our expected Runtime
        assert session.name.startswith(
            runtime_name + "/sessions/"
        )

        # GET
        retrieved = sessions_api.get(
            name=session.name,
        )

        print(
            "Retrieved:",
            retrieved.name,
        )

        assert retrieved.name == session.name

        # LIST
        sessions = list(
            sessions_api.list(
                name=runtime_name,
            )
        )

        print(
            "Listed session count:",
            len(sessions),
        )

        assert any(
            item.name == session.name
            for item in sessions
        ), (
            "Created session was not returned by "
            "the Runtime session list"
        )

    finally:

        # DELETE
        if (
            session is not None
            and "/operations/" not in session.name
        ):
            sessions_api.delete(
                name=session.name,
            )

            print(
                "Deleted:",
                session.name,
            )