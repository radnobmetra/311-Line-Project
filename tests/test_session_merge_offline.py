"""Offline regression tests for PR #126 + #135 session-handling integration.

Place this file in the repository's tests/ directory and run:
    python -m unittest discover -s tests -p test_session_merge_offline.py -v

The tests load only function definitions from the real source with ast to avoid
import-time authentication and cloud clients. All external calls are mocked.
"""
import ast
import hashlib
import os
from pathlib import Path
import sys
import types
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent
if not (PROJECT_ROOT / "session_handling.py").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent


def extract_code(filename, functions=(), variables=()):
    tree = ast.parse((PROJECT_ROOT / filename).read_text(encoding="utf-8-sig"), filename=filename)
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in functions:
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in variables for target in node.targets
        ):
            selected.append(node)
    return compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])), filename, "exec")


HANDLER_CODE = extract_code("session_handling.py", functions=(
    "get_update_time", "get_event_text", "has_resolved_state", "mark_session_resolved",
    "mark_inactive_sessions", "create_update_agent_session", "_session_name",
))
MANUAL_CODE = extract_code("manual_311_evaluations.py", functions=(
    "is_selected", "scan_sessions", "current_events_allow_processing", "run_batch",
), variables=("SAMPLE_RATE", "INACTIVITY_SECONDS", "DONE_MARKERS"))


class FakeStore:
    def __init__(self):
        self.sessions_by_id = {}
        self.events_by_id = {}
        self.appended = []
        self.next_id = 1

    def session(self, sid, age=3600):
        s = types.SimpleNamespace(name=f"reasoningEngines/demo/sessions/{sid}",
                                  update_time=datetime.now(timezone.utc) - timedelta(seconds=age))
        self.sessions_by_id[sid] = s
        self.events_by_id.setdefault(sid, [])
        return s

    def event(self, sid, author, text="", actions=None):
        event = types.SimpleNamespace(
            author=author, timestamp=datetime.now(timezone.utc),
            content=types.SimpleNamespace(parts=[types.SimpleNamespace(text=text)]),
            actions=types.SimpleNamespace(state_delta=actions) if actions is not None else None)
        self.events_by_id.setdefault(sid, []).append(event)
        return event

    def append(self, **kwargs):
        sid = kwargs["name"].rsplit("/", 1)[-1]
        config = kwargs.get("config", {})
        content = config.get("content", {})
        text = "".join(part.get("text", "") for part in content.get("parts", []))
        state = config.get("actions", {}).get("state_delta")
        event = self.event(sid, kwargs["author"], text, state)
        self.appended.append((sid, event))
        return event

    def authors(self, sid):
        return [event.author for event in self.events_by_id.get(sid, [])]

    def count_resolved(self, sid):
        return sum(getattr(getattr(e, "actions", None), "state_delta", None) == {"status": "resolved", "outcome_label": "session timeout"}
                   for e in self.events_by_id.get(sid, []))


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.store = FakeStore()
        self.eval_calls = []
        self.fake_eval_module = types.ModuleType("evaluation_handling")

        def fake_evaluator(sid):
            self.eval_calls.append(sid)
            self.store.event(sid, "eval_author", "score")
            return {"score": 1}

        self.fake_eval_module.evaluate_completed_session = fake_evaluator
        self.handler = {
            "os": os, "uuid": uuid, "datetime": datetime, "timezone": timezone,
            "client": types.SimpleNamespace(sessions=types.SimpleNamespace(
                events=types.SimpleNamespace(append=self.store.append))),
            "list_events": lambda sid: list(self.store.events_by_id.get(sid, [])),
            "list_sessions": lambda: list(self.store.sessions_by_id.values()),
            "get_session": lambda sid: self.store.sessions_by_id[sid],
        }
        self.original_engine_id = os.environ.get("SESSION_AGENT_ENGINE_ID")
        os.environ["SESSION_AGENT_ENGINE_ID"] = "demo"
        self.eval_patch = patch.dict(sys.modules, {"evaluation_handling": self.fake_eval_module})
        self.eval_patch.start()

        def create_session(user_Number, source):
            sid = f"new-{self.store.next_id}"
            self.store.next_id += 1
            self.store.session(sid, age=0)
            return sid

        self.handler["create_session"] = create_session
        self.handler["list_users_sessions"] = lambda user_Number, source: list(self.store.sessions_by_id.values())
        self.handler["add_custom_event"] = lambda author, value, sid: self.store.event(sid, author, str(value))
        exec(HANDLER_CODE, self.handler)
        self.manual = {
            "sh": types.SimpleNamespace(
                list_sessions=self.handler["list_sessions"],
                list_events=self.handler["list_events"],
                get_session=self.handler["get_session"],
                get_update_time=self.handler["get_update_time"],
                mark_session_resolved=self.handler["mark_session_resolved"],
                add_custom_event=self.handler["add_custom_event"]),
            "datetime": datetime, "timezone": timezone, "hashlib": hashlib,
        }
        exec(MANUAL_CODE, self.manual)

    def tearDown(self):
        self.eval_patch.stop()
        if self.original_engine_id is None:
            os.environ.pop("SESSION_AGENT_ENGINE_ID", None)
        else:
            os.environ["SESSION_AGENT_ENGINE_ID"] = self.original_engine_id

    def test_mark_resolved_adds_state_delta(self):
        self.store.session("old")
        self.store.event("old", "user", "hi")
        self.assertTrue(self.handler["mark_session_resolved"]("old"))
        self.assertEqual(self.store.count_resolved("old"), 1)

    def test_mark_resolved_idempotent(self):
        self.store.session("old")
        self.store.event("old", "user")
        self.handler["mark_session_resolved"]("old")
        self.handler["mark_session_resolved"]("old")
        self.assertEqual(self.store.count_resolved("old"), 1)

    def test_timeout_text_alone_does_not_count_as_resolved_state(self):
        self.store.session("old")
        self.store.event("old", "session_timeout", "closed: timeout")
        self.handler["mark_session_resolved"]("old")
        self.assertEqual(self.store.count_resolved("old"), 1)

    def test_active_session_reused(self):
        self.store.session("old", age=10)
        self.store.event("old", "user")
        self.assertEqual(self.handler["create_update_agent_session"]("user", 1800, "sms"), "old")

    def test_expired_session_new_session_and_both_markers(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        new_id = self.handler["create_update_agent_session"]("user", 1800, "sms")
        self.assertNotEqual(new_id, "old")
        self.assertIn("session_timeout", self.store.authors("old"))
        self.assertEqual(self.store.count_resolved("old"), 1)

    def test_previously_resolved_session_not_reused(self):
        self.store.session("old", age=3)
        self.store.event("old", "user")
        self.handler["mark_session_resolved"]("old")
        self.assertNotEqual(self.handler["create_update_agent_session"]("user", 1800, "sms"), "old")

    def test_inactive_session_closes_with_both_markers(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        with patch.dict(os.environ, {"EVALUATION_SAMPLE_RATE": "0"}):
            self.assertEqual(self.handler["mark_inactive_sessions"](1800), 1)
        self.assertEqual(self.store.count_resolved("old"), 1)
        self.assertEqual(self.store.authors("old").count("session_timeout"), 1)
        self.assertEqual(self.store.authors("old").count("evaluation_skipped"), 1)

    def test_repeat_inactivity_does_not_duplicate_closure(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        with patch.dict(os.environ, {"EVALUATION_SAMPLE_RATE": "0"}):
            self.handler["mark_inactive_sessions"](1800)
            self.handler["mark_inactive_sessions"](1800)
        self.assertEqual(self.store.count_resolved("old"), 1)
        self.assertEqual(self.store.authors("old").count("session_timeout"), 1)

    def test_active_session_is_not_closed(self):
        self.store.session("new", age=60)
        self.store.event("new", "user")
        with patch.dict(os.environ, {"EVALUATION_SAMPLE_RATE": "0"}):
            self.assertEqual(self.handler["mark_inactive_sessions"](1800), 0)
        self.assertEqual(self.store.count_resolved("new"), 0)

    def test_session_without_user_marked_skipped(self):
        self.store.session("test", age=3600)
        self.store.event("test", "agent", "hello")
        with patch.dict(os.environ, {"EVALUATION_SAMPLE_RATE": "0"}):
            self.handler["mark_inactive_sessions"](1800)
        self.assertEqual(self.store.count_resolved("test"), 1)
        self.assertIn("evaluation_skipped", self.store.authors("test"))

    def test_timeout_marker_without_resolved_state_is_reconciled(self):
        """Regression: old #135 session_timeout markers must not block #126 state."""
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        self.store.event("old", "session_timeout", "closed: timeout")
        with patch.dict(os.environ, {"EVALUATION_SAMPLE_RATE": "0"}):
            self.handler["mark_inactive_sessions"](1800)
        self.assertEqual(self.store.count_resolved("old"), 1)

    def test_preview_is_read_only_and_selects_inactive_only(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        self.store.session("new", age=100)
        self.store.event("new", "user")
        candidates, counts = self.manual["scan_sessions"]()
        self.assertEqual([c["id"] for c in candidates], ["old"])
        self.assertEqual(counts["still_active"], 1)
        self.assertEqual(self.store.appended, [])

    def test_manual_batch_skips_without_paid_evaluation(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        self.manual["run_batch"]([{"id": "old", "selected": False, "no_user": False}], 1)
        self.assertEqual(self.store.count_resolved("old"), 1)
        self.assertIn("session_timeout", self.store.authors("old"))
        self.assertIn("evaluation_skipped", self.store.authors("old"))
        self.assertEqual(self.eval_calls, [])

    def test_manual_batch_evaluates_selected_once(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        candidate = {"id": "old", "selected": True, "no_user": False}
        self.manual["run_batch"]([candidate], 1)
        self.manual["run_batch"]([candidate], 1)
        self.assertEqual(self.eval_calls, ["old"])
        self.assertEqual(self.store.count_resolved("old"), 1)
        self.assertEqual(self.store.authors("old").count("evaluation_attempted"), 1)

    def test_manual_batch_deferred_selected_is_not_marked_attempted(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        self.manual["run_batch"]([{"id": "old", "selected": True, "no_user": False}], 0)
        self.assertIn("session_timeout", self.store.authors("old"))
        self.assertEqual(self.store.count_resolved("old"), 1)
        self.assertNotIn("evaluation_attempted", self.store.authors("old"))

    def test_done_marker_prevents_manual_reprocessing(self):
        self.store.session("old", age=3600)
        self.store.event("old", "user")
        self.store.event("old", "evaluation_attempted")
        candidates, counts = self.manual["scan_sessions"]()
        self.assertEqual(candidates, [])
        self.assertEqual(counts["already_handled"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
