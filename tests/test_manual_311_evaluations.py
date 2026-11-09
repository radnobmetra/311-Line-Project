"""Offline unit tests for manual_311_evaluations.py.

Run from the project root:
    python -m pytest tests/test_manual_311_evaluations.py -v

The test replaces Google session access and evaluation calls with in-memory fakes.
No Google credentials, Cloud API calls, session writes, or paid evaluations.
"""

import contextlib
import hashlib
import importlib.util
import io
import sys
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


def forbidden_cloud_call(*args, **kwargs):
    raise AssertionError("Unexpected real Google Cloud call")


fake_session_handling = types.ModuleType("session_handling")
for name in (
    "list_sessions", "list_events", "get_update_time", "get_session",
    "add_custom_event",
):
    setattr(fake_session_handling, name, forbidden_cloud_call)

script_path = Path(__file__).resolve().parent.parent / "manual_311_evaluations.py"
if not script_path.is_file():
    raise FileNotFoundError(
        "manual_311_evaluations.py not found in expected location"
    )

spec = importlib.util.spec_from_file_location("_manual_311_under_test", script_path)
batch = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"session_handling": fake_session_handling}):
    spec.loader.exec_module(batch)


class FakeCloud:
    """Only in-memory sessions/events. No external APIs."""

    def __init__(self):
        self.sessions = {}
        self.events = {}
        self.writes = []

    def add_session(self, session_id, *, age_minutes=90, authors=("user", "OverseerAgent")):
        self.sessions[session_id] = types.SimpleNamespace(
            name=f"projects/fake/locations/us/reasoningEngines/fake/sessions/{session_id}",
            user_id="fake-user",
            updated=datetime.now(timezone.utc) - timedelta(minutes=age_minutes),
        )
        self.events[session_id] = [types.SimpleNamespace(author=a) for a in authors]

    def list_sessions(self):
        return list(self.sessions.values())

    def list_events(self, session_id):
        return list(self.events[session_id])

    def get_update_time(self, session):
        return session.updated

    def get_session(self, session_id):
        return self.sessions[session_id]

    def add_custom_event(self, author, custom_data, session_id):
        self.writes.append((author, custom_data, session_id))
        self.events[session_id].append(types.SimpleNamespace(author=author))
        return True


class TestManualEvaluations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chosen = []
        rejected = []
        for index in range(10000):
            session_id = f"fake-conversation-{index}"
            (chosen if batch.is_selected(session_id) else rejected).append(session_id)
            if len(chosen) >= 3 and len(rejected) >= 3:
                break
        if len(chosen) < 3 or len(rejected) < 3:
            raise AssertionError("Could not construct sample test session IDs")
        cls.selected_ids = chosen[:3]
        cls.unselected_ids = rejected[:3]

    def setUp(self):
        self.fake = FakeCloud()
        self.patches = [
            patch.object(batch.sh, "list_sessions", self.fake.list_sessions),
            patch.object(batch.sh, "list_events", self.fake.list_events),
            patch.object(batch.sh, "get_update_time", self.fake.get_update_time),
            patch.object(batch.sh, "get_session", self.fake.get_session),
            patch.object(batch.sh, "add_custom_event", self.fake.add_custom_event),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def fake_evaluator(self, callback):
        module = types.ModuleType("evaluation_handling")
        module.evaluate_completed_session = callback
        return patch.dict(sys.modules, {"evaluation_handling": module})

    def run_and_capture(self, candidates, maximum=1):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            batch.run_batch(candidates, max_evaluations=maximum)
        return output.getvalue()

    def test_deterministic_sample_rate_is_ten_percent(self):
        ids = [f"rate-check-{i}" for i in range(2000)]
        selected = sum(batch.is_selected(session_id) for session_id in ids)
        self.assertGreater(selected, 140)
        self.assertLess(selected, 260)
        for session_id in ids[:20]:
            expected = (
                int.from_bytes(
                    hashlib.sha256(session_id.encode("utf-8")).digest()[:8], "big"
                ) / (1 << 64) < 0.10
            )
            self.assertEqual(batch.is_selected(session_id), expected)

    def test_scan_skips_active_empty_locks_and_already_processed(self):
        selected = self.selected_ids[0]
        rejected = self.unselected_ids[0]
        self.fake.add_session(selected)
        self.fake.add_session(rejected)
        self.fake.add_session("young", age_minutes=1)
        self.fake.add_session("empty", authors=())
        self.fake.add_session("already-done", authors=("user", "evaluation_attempted"))
        self.fake.add_session("no-user", authors=("OverseerAgent",))
        self.fake.add_session("eval-lock-test")

        with contextlib.redirect_stdout(io.StringIO()):
            candidates, counts = batch.scan_sessions()

        by_id = {entry["id"]: entry for entry in candidates}
        self.assertEqual(set(by_id), {selected, rejected, "no-user"})
        self.assertTrue(by_id[selected]["selected"])
        self.assertFalse(by_id[rejected]["selected"])
        self.assertTrue(by_id["no-user"]["no_user"])
        self.assertEqual(counts["locks"], 1)
        self.assertEqual(counts["empty"], 1)
        self.assertEqual(counts["already_handled"], 1)
        self.assertEqual(counts["still_active"], 1)
        self.assertEqual(self.fake.writes, [])

    def test_run_evaluates_selected_saves_score_and_skips_rest(self):
        selected = self.selected_ids[0]
        rejected = self.unselected_ids[0]
        self.fake.add_session(selected)
        self.fake.add_session(rejected)
        calls = []

        def fake_evaluate(session_id):
            calls.append(session_id)
            self.fake.add_custom_event("eval_author", '{"score": 0.85}', session_id)
            return {"score": 0.85}

        with contextlib.redirect_stdout(io.StringIO()):
            candidates, _ = batch.scan_sessions()
        with self.fake_evaluator(fake_evaluate):
            result = self.run_and_capture(candidates, maximum=1)

        self.assertEqual(calls, [selected])
        self.assertIn("Evaluations saved: 1", result)
        self.assertIn("Evaluation attempts: 1", result)
        self.assertIn("Sessions skipped: 1", result)
        self.assertIn("eval_author", [e.author for e in self.fake.events[selected]])
        self.assertIn("evaluation_attempted", [e.author for e in self.fake.events[selected]])
        self.assertIn("evaluation_skipped", [e.author for e in self.fake.events[rejected]])

    def test_max_one_defers_other_selected_sessions(self):
        first, second = sorted(self.selected_ids[:2])
        self.fake.add_session(first)
        self.fake.add_session(second)
        calls = []

        def fake_evaluate(session_id):
            calls.append(session_id)
            self.fake.add_custom_event("eval_author", '{"score": 1.0}', session_id)
            return {"score": 1.0}

        with contextlib.redirect_stdout(io.StringIO()):
            candidates, _ = batch.scan_sessions()
        with self.fake_evaluator(fake_evaluate):
            result = self.run_and_capture(candidates, maximum=1)

        self.assertEqual(calls, [first])
        self.assertIn("Selected sessions deferred for future runs: 1", result)
        self.assertNotIn("evaluation_attempted", [e.author for e in self.fake.events[second]])
        self.assertNotIn("evaluation_skipped", [e.author for e in self.fake.events[second]])

    def test_failed_evaluation_is_not_retried(self):
        selected = self.selected_ids[0]
        self.fake.add_session(selected)
        calls = []

        def fake_evaluate(session_id):
            calls.append(session_id)
            return None  # Simulate service failure after recording attempt.

        with contextlib.redirect_stdout(io.StringIO()):
            candidates, _ = batch.scan_sessions()
        with self.fake_evaluator(fake_evaluate):
            first_result = self.run_and_capture(candidates)
            second_result = self.run_and_capture(candidates)

        self.assertEqual(calls, [selected])
        self.assertIn("No result / failures: 1", first_result)
        self.assertIn(f"ALREADY HANDLED: {selected}", second_result)

    def test_preview_main_does_not_run_batch_or_prompt(self):
        selected = self.selected_ids[0]
        self.fake.add_session(selected)
        with (
            patch.object(sys, "argv", ["manual_311_evaluations.py"]),
            patch.object(batch, "run_batch", side_effect=AssertionError("Executed a batch!")),
            patch("builtins.input", side_effect=AssertionError("Prompted in preview!")),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            batch.main()
        self.assertIn("PREVIEW ONLY", output.getvalue())
        self.assertEqual(self.fake.writes, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
