"""Manually process completed Sacramento 311 sessions with 10% sampling.

Run from the 311-Line-Project root, using its .venv:

    python manual_311_evaluations.py
    python manual_311_evaluations.py --run --max-evaluations 1

Default is read-only preview. This script uses the *local* ADC service
account and the existing evaluation_handling.evaluate_completed_session().
Before use, disable ENABLE_MANAGED_SESSION_TIMER in deployed Agent Runtime.
"""

import argparse
import hashlib
from datetime import datetime, timezone

import session_handling as sh

SAMPLE_RATE = 0.10
INACTIVITY_SECONDS = 1800  # 30 minutes, matching timerloop.py
DONE_MARKERS = frozenset({
    "eval_author",
    "evaluation_skipped",
    "evaluation_attempted",
    "evaluation_error",
})


def is_selected(session_id):
    """Match the existing mark_inactive_sessions deterministic 10% rule."""
    first_eight_bytes = hashlib.sha256(session_id.encode("utf-8")).digest()[:8]
    value = int.from_bytes(first_eight_bytes, "big")
    return value / (1 << 64) < SAMPLE_RATE


def scan_sessions():
    """Read session metadata and events; make NO writes or evaluations."""
    now = datetime.now(timezone.utc)
    candidates = []
    counts = {"locks": 0, "empty": 0, "already_handled": 0,
              "still_active": 0, "no_user": 0}

    sessions = sh.list_sessions()
    print(f"Discovered {len(sessions)} managed sessions.", flush=True)

    for session in sessions:
        session_id = session.name.rsplit("/", 1)[-1]
        if session_id.startswith("eval-lock-"):
            counts["locks"] += 1
            continue

        events = sh.list_events(session_id)
        if not events:
            counts["empty"] += 1
            continue

        authors = {event.author for event in events}
        if authors & DONE_MARKERS:
            counts["already_handled"] += 1
            continue

        timed_out = "session_timeout" in authors
        age_seconds = (now - sh.get_update_time(session)).total_seconds()
        if not timed_out and age_seconds < INACTIVITY_SECONDS:
            counts["still_active"] += 1
            continue

        # Like the existing timer, don't spend money on sessions with no user.
        if "user" not in authors:
            counts["no_user"] += 1
            candidates.append({"id": session_id, "selected": False,
                               "timed_out": timed_out, "no_user": True})
            continue

        candidates.append({"id": session_id,
                           "selected": is_selected(session_id),
                           "timed_out": timed_out, "no_user": False})

    candidates.sort(key=lambda item: item["id"])
    return candidates, counts


def current_events_allow_processing(session_id):
    """Recheck before writing, to avoid stale preview data."""
    events = sh.list_events(session_id)
    authors = {event.author for event in events}
    if not events or authors & DONE_MARKERS:
        return None
    return authors


def run_batch(candidates, max_evaluations):
    from evaluation_handling import evaluate_completed_session

    attempted = 0
    successful = 0
    skipped = 0
    deferred = 0
    failures = 0

    for item in candidates:
        session_id = item["id"]
        authors = current_events_allow_processing(session_id)
        if authors is None:
            print(f"ALREADY HANDLED: {session_id}")
            continue

        # Check inactivity before closing the session.
        if "session_timeout" not in authors:
            current_session = sh.get_session(session_id)
            age = (
                datetime.now(timezone.utc)
                - sh.get_update_time(current_session)
            ).total_seconds()

            if age < INACTIVITY_SECONDS:
                print(f"STILL ACTIVE: {session_id}")
                continue

        sh.mark_session_resolved(session_id)

        # Preserve the timeout marker used by manual evaluation.
        if "session_timeout" not in authors:
            sh.add_custom_event(
                "session_timeout",
                "closed: timeout",
                session_id
            )

        if item["no_user"] or not item["selected"]:
            reason = "no_user_messages" if item["no_user"] else "not_selected_for_sampling"
            sh.add_custom_event("evaluation_skipped", reason, session_id)
            skipped += 1
            print(f"SKIPPED: {session_id} ({reason})", flush=True)
            continue

        if attempted >= max_evaluations:
            deferred += 1
            print(f"DEFERRED: {session_id} (evaluation limit reached)", flush=True)
            continue

        # Prevent a second run from repeating this session, even after a failure.
        sh.add_custom_event("evaluation_attempted", "started: manual_batch", session_id)
        attempted += 1
        print(f"EVALUATING {attempted}/{max_evaluations}: {session_id}", flush=True)

        try:
            # Existing implementation acquires eval-lock-<hash> before paid API.
            result = evaluate_completed_session(session_id)
            if result is None:
                failures += 1
                print(f"NO RESULT: {session_id} (do not retry automatically)", flush=True)
            else:
                result_authors = {e.author for e in sh.list_events(session_id)}
                if "eval_author" in result_authors:
                    successful += 1
                    print(f"SAVED: {session_id}; score={result.get('score')}", flush=True)
                else:
                    failures += 1
                    print(f"NOT SAVED: {session_id} (do not retry)", flush=True)
        except Exception as error:
            failures += 1
            print(f"FAILED: {session_id}: {type(error).__name__}: {str(error)[:350]}")
            print("Do not retry this session automatically.")

    print("\n=== BATCH FINISHED ===")
    print(f"Evaluation attempts: {attempted}")
    print(f"Evaluations saved: {successful}")
    print(f"No result / failures: {failures}")
    print(f"Sessions skipped: {skipped}")
    print(f"Selected sessions deferred for future runs: {deferred}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true",
                        help="Write markers and perform selected evaluations (potentially paid)")
    parser.add_argument("--max-evaluations", type=int, default=1,
                        help="Cap evaluation attempts in this run (default: 1)")
    args = parser.parse_args()
    if args.max_evaluations < 1:
        parser.error("--max-evaluations must be at least 1")

    print("=== MANUAL 311 EVALUATION BATCH ===")
    print("Mode:", "RUN (writes + possible charges)" if args.run else "PREVIEW (read-only)")
    print("Sampling: 10% deterministic, matching mark_inactive_sessions")
    print("Inactivity threshold: 30 minutes")
    print("Maximum evaluation attempts this run:", args.max_evaluations)
    print("IMPORTANT: Deployed ENABLE_MANAGED_SESSION_TIMER must be 0.\n")

    candidates, counts = scan_sessions()
    chosen = [c for c in candidates if c["selected"] and not c["no_user"]]
    skipped = len(candidates) - len(chosen)

    print("\n=== READ-ONLY PREVIEW ===")
    print(f"Already processed/attempted/skipped: {counts['already_handled']}")
    print(f"Lock sessions ignored: {counts['locks']}")
    print(f"Empty sessions ignored: {counts['empty']}")
    print(f"Not yet inactive: {counts['still_active']}")
    print(f"Eligible sessions awaiting decision: {len(candidates)}")
    print(f"Selected by 10% rule: {len(chosen)}")
    print(f"To mark skipped (including no-user sessions): {skipped}")
    print(f"Would attempt now, at most: {min(len(chosen), args.max_evaluations)}")
    for item in chosen[:20]:
        print("  SELECTED:", item["id"])
    if len(chosen) > 20:
        print(f"  ... and {len(chosen) - 20} more")

    if not args.run:
        print("\nPREVIEW ONLY. No session writes or paid evaluation calls.")
        print("To run: python manual_311_evaluations.py --run --max-evaluations 1")
        return

    if not candidates:
        print("\nNothing eligible to process.")
        return

    answer = input("\nType RUN MANUAL BATCH to write markers and evaluate selected sessions: ")
    if answer != "RUN MANUAL BATCH":
        print("Cancelled. No session writes or paid evaluation calls.")
        return

    run_batch(candidates, args.max_evaluations)


if __name__ == "__main__":
    main()
