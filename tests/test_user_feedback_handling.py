"""Unit tests for user_feedback_handling.py.

Run from the project root:
    python -m pytest -q tests/test_user_feedback_handling.py
these tests do not submit real feedback.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

# Match remote_chat.py: load the project's environment before importing the
# feedback module (which constructs RUNTIME_NAME during import).
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

import user_feedback_handling as feedback  # noqa: E402


@pytest.fixture
def feedback_api(monkeypatch):
    """Replace the Cloud client for this test only."""
    fake_client = Mock()
    monkeypatch.setattr(feedback, "client", fake_client)
    return fake_client.feedback_entries


def make_event(event_id, text, *, author="OverseerAgent", invocation_id="inv-1"):
    """Small stand-in for the saved ADK events returned by list_events()."""
    return SimpleNamespace(
        author=author,
        invocation_id=invocation_id,
        raw_event={"id": event_id},
        content=SimpleNamespace(parts=[SimpleNamespace(text=text)]),
    )


def make_feedback_entry(
    name,
    *,
    session_id="session-1",
    event_id="event-1",
    user_id="user-1",
    update_time="2026-10-11T18:00:00Z",
):
    return SimpleNamespace(
        name=name,
        session_id=session_id,
        event_id=event_id,
        user_id=user_id,
        update_time=update_time,
    )


@pytest.mark.parametrize(
    ("rating", "expected"),
    [("up", "THUMBS_UP"), ("down", "THUMBS_DOWN")],
)
def test_feedback_type_from_rating(rating, expected):
    assert feedback.feedback_type_from_rating(rating) == expected


@pytest.mark.parametrize("rating", ["", "like", "UP", "neutral"])
def test_feedback_type_rejects_invalid_rating(rating):
    with pytest.raises(ValueError, match="Rating must be"):
        feedback.feedback_type_from_rating(rating)


def test_save_feedback_sends_correct_fields(feedback_api):
    saved = make_feedback_entry("feedback-1")
    feedback_api.create.return_value.response = saved

    result = feedback.save_feedback(
        session_id="session-1",
        event_id="event-1",
        rating="down",
        user_id="user-1",
        comment="This was unclear",
        labels=["unclear"],
    )

    assert result is saved
    feedback_api.create.assert_called_once_with(
        name=feedback.RUNTIME_NAME,
        session_id="session-1",
        event_id="event-1",
        feedback_type="THUMBS_DOWN",
        config={
            "feedback_text": "This was unclear",
            "feedback_labels": ["unclear"],
            "user_id": "user-1",
            "source": "311-chat-ui",
        },
    )


@pytest.mark.parametrize("missing_field", ["session_id", "event_id", "user_id"])
def test_save_feedback_requires_identifiers(feedback_api, missing_field):
    arguments = {
        "session_id": "session-1",
        "event_id": "event-1",
        "rating": "up",
        "user_id": "user-1",
    }
    arguments[missing_field] = ""

    with pytest.raises(ValueError, match="required"):
        feedback.save_feedback(**arguments)

    feedback_api.create.assert_not_called()


def test_save_feedback_rejects_missing_cloud_response(feedback_api):
    feedback_api.create.return_value.response = None

    with pytest.raises(RuntimeError, match="did not return an entry"):
        feedback.save_feedback("session-1", "event-1", "up", "user-1")


def test_get_feedback_uses_feedback_name(feedback_api):
    saved = make_feedback_entry("feedback-1")
    feedback_api.get.return_value = saved

    assert feedback.get_feedback("feedback-1") is saved
    feedback_api.get.assert_called_once_with(name="feedback-1")


def test_update_feedback_updates_existing_entry(feedback_api):
    updated = make_feedback_entry("feedback-1")
    feedback_api.update.return_value.response = updated

    result = feedback.update_feedback(
        feedback_name="feedback-1",
        rating="down",
        comment="Missing details",
        labels=["incomplete"],
    )

    assert result is updated
    feedback_api.update.assert_called_once_with(
        name="feedback-1",
        config={
            "feedback_type": "THUMBS_DOWN",
            "feedback_text": "Missing details",
            "feedback_labels": ["incomplete"],
            "update_mask": "feedbackType,feedbackText,feedbackLabels",
        },
    )
    feedback_api.create.assert_not_called()


def test_update_feedback_rejects_missing_cloud_response(feedback_api):
    feedback_api.update.return_value.response = None

    with pytest.raises(RuntimeError, match="did not return a completed entry"):
        feedback.update_feedback("feedback-1", "up")


def test_two_responses_create_two_distinct_entries(feedback_api):
    """Separate response event IDs must be passed to separate create calls."""

    def fake_create(**kwargs):
        event_id = kwargs["event_id"]
        return SimpleNamespace(
            response=make_feedback_entry(
                f"feedback-for-{event_id}", event_id=event_id
            )
        )

    feedback_api.create.side_effect = fake_create

    first = feedback.save_feedback("session-1", "event-1", "up", "user-1")
    second = feedback.save_feedback("session-1", "event-2", "down", "user-1")

    assert first.name != second.name
    assert first.event_id == "event-1"
    assert second.event_id == "event-2"
    assert feedback_api.create.call_count == 2


def test_find_response_event_id_matches_actual_displayed_answer(monkeypatch):
    events = [
        make_event("old-event", "The answer", invocation_id="inv-old"),
        make_event("wrong-author", "The answer", author="QAReviewerAgent"),
        make_event("wrong-text", "Different answer"),
        make_event("correct-event", "The answer", author="QAAgent"),
    ]
    monkeypatch.setattr(feedback, "list_events", lambda session_id: events)

    event_id = feedback.find_response_event_id(
        "session-1",
        {"author": "QAAgent", "invocationId": "inv-1", "id": "correct-event"},
        "The answer",
    )

    assert event_id == "correct-event"


def test_find_response_event_id_rejects_nonmatching_answer(monkeypatch):
    monkeypatch.setattr(
        feedback,
        "list_events",
        lambda session_id: [make_event("event-1", "A different answer")],
    )

    with pytest.raises(RuntimeError, match="Found 0 matches"):
        feedback.find_response_event_id(
            "session-1",
            {"author": "OverseerAgent", "invocationId": "inv-1"},
            "The answer shown to the user",
        )


def test_find_response_event_id_rejects_ambiguous_match(monkeypatch):
    monkeypatch.setattr(
        feedback,
        "list_events",
        lambda session_id: [
            make_event("event-1", "Same answer"),
            make_event("event-2", "Same answer"),
        ],
    )

    with pytest.raises(RuntimeError, match="Found 2 matches"):
        feedback.find_response_event_id(
            "session-1",
            {"author": "OverseerAgent", "invocationId": "inv-1"},
            "Same answer",
        )


def test_find_response_event_id_requires_response(monkeypatch):
    fake_list = Mock()
    monkeypatch.setattr(feedback, "list_events", fake_list)

    with pytest.raises(ValueError, match="No valid agent response"):
        feedback.find_response_event_id("session-1", {}, "")

    fake_list.assert_not_called()


def test_find_existing_feedback_matches_all_three_ids(feedback_api):
    wrong_user = make_feedback_entry("wrong-user", user_id="someone-else")
    wrong_event = make_feedback_entry("wrong-event", event_id="another-event")
    wrong_session = make_feedback_entry("wrong-session", session_id="another-session")
    matching = make_feedback_entry("matching-entry")
    feedback_api.list.return_value = [
        wrong_user, wrong_event, wrong_session, matching
    ]

    result = feedback.find_existing_feedback("session-1", "event-1", "user-1")

    assert result is matching
    feedback_api.list.assert_called_once_with(parent=feedback.RUNTIME_NAME)


def test_find_existing_feedback_returns_latest_duplicate(feedback_api):
    earlier = make_feedback_entry(
        "older", update_time="2026-10-11T18:00:00Z"
    )
    later = make_feedback_entry(
        "newer", update_time="2026-10-11T19:00:00Z"
    )
    feedback_api.list.return_value = [earlier, later]

    assert feedback.find_existing_feedback("session-1", "event-1", "user-1") is later


def test_find_existing_feedback_returns_none_when_absent(feedback_api):
    feedback_api.list.return_value = [
        make_feedback_entry("unrelated", event_id="event-2")
    ]

    assert feedback.find_existing_feedback("session-1", "event-1", "user-1") is None
