
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import manual_311_evaluations as manual
import evaluation_handling as evaluation


def make_event(author, payload=None):
    parts = [] if payload is None else [
        SimpleNamespace(text=json.dumps(payload))
    ]
    return SimpleNamespace(
        author=author,
        content=SimpleNamespace(parts=parts)
    )


def test_manual_batch_combines_and_saves(monkeypatch):
    # Find an ID that passes the real 10% sampling rule.
    session_id = next(
        f"manual-test-{n}"
        for n in range(1000)
        if manual.is_selected(f"manual-test-{n}")
    )

    # Simulate an inactive session from the deployed runtime.
    session = SimpleNamespace(
        name=f"sessions/{session_id}",
        updated=datetime.now(timezone.utc) - timedelta(hours=1)
    )

    events = [
        make_event("user"),
        make_event("agent"),
        make_event("user_feedback", {
            "event_id": "answer-1",
            "user_id": "resident-1",
            "rating": "up"
        })
    ]

    saved = []

    # Replace external session storage with in-memory records.
    monkeypatch.setattr(
        manual.sh, "list_sessions", lambda: [session]
    )
    monkeypatch.setattr(
        manual.sh, "list_events", lambda sid: list(events)
    )
    monkeypatch.setattr(
        manual.sh, "get_session", lambda sid: session
    )
    monkeypatch.setattr(
        manual.sh, "get_update_time", lambda s: s.updated
    )

    close_session = Mock(return_value=True)
    monkeypatch.setattr(
        manual.sh, "mark_session_resolved", close_session
    )

    def fake_add_custom_event(author, custom_data, session_ID):
        assert str(session_ID) == session_id

        events.append(make_event(author))

        if author == "eval_author":
            saved.append(json.loads(custom_data))

        return True

    monkeypatch.setattr(
        manual.sh, "add_custom_event", fake_add_custom_event
    )

    # Simulate Google's evaluation response.
    # Keep the project's real combination and saving functions.
    def fake_evaluate(sid):
        result = {"score": 0.9, "session_id": sid}
        evaluation.save_combined_session_results(
            str(sid), result
        )
        return result

    evaluate = Mock(side_effect=fake_evaluate)
    monkeypatch.setattr(
        evaluation, "evaluate_completed_session", evaluate
    )

    # Test the actual manual session selection.
    candidates, _ = manual.scan_sessions()

    assert len(candidates) == 1
    assert candidates[0]["selected"] is True

    # Preview must not write to session storage.
    assert saved == []
    close_session.assert_not_called()

    # Execute the actual manual batch function.
    manual.run_batch(candidates, max_evaluations=1)

    evaluate.assert_called_once_with(session_id)
    close_session.assert_called_once_with(session_id)

    # Check the saved combined result.
    assert len(saved) == 1

    combined = saved[0]

    assert combined["ai_evaluation"] == {"score": 0.9}
    assert combined["user_feedback"] == {
        "thumbs_up": 1,
        "thumbs_down": 0,
        "rating": "thumbs_up"
    }
    assert combined["final_outcome"] == "HELPED"

    # Make sure rerunning does not duplicate the evaluation.
    manual.run_batch(candidates, max_evaluations=1)

    evaluate.assert_called_once()
    assert len(saved) == 1

    print("\n--- MANUAL 311 EVALUATION ---")
    print(f"Selected session: {session_id}")
    print("AI evaluation score (mocked): 0.9")
    print(f"User feedback: {combined['user_feedback']}")
    print(f"Combined outcome: {combined['final_outcome']}")
    print("Saved eval_author event: True")
    print("Duplicate evaluation prevented: True")


@pytest.mark.parametrize(
    "score,rating,expected",
    [
        (0.9, "up", "HELPED"),
        (0.9, "down", "UNCLEAR"),
        (0.2, "down", "NOT_HELPED"),
        (0.9, None, "UNCLEAR")
    ]
)
def test_combined_outcome_rules(
    monkeypatch, score, rating, expected
):
    # Simulate feedback stored in a session.
    events = [] if rating is None else [
        make_event("user_feedback", {
            "event_id": "answer-1",
            "user_id": "resident-1",
            "rating": rating
        })
    ]

    monkeypatch.setattr(
        evaluation.session_handling,
        "list_events",
        lambda sid: events
    )

    # Execute the actual combination logic.
    combined = evaluation.combine_session_results(
        "test-session",
        {"score": score}
    )

    assert combined["final_outcome"] == expected

    print(
        f"AI score: {score}, "
        f"Feedback: {rating}, "
        f"Final outcome: {expected}"
    )
