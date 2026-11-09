import logging
import os
import time

CHECK_INTERVAL_SECONDS = 60
SESSION_TTL_SECONDS = 1800


def run_loop():
    """Periodically close inactive Google-managed sessions."""

    logging.info("Managed session inactivity timer started")

    while os.environ.get("ENABLE_MANAGED_SESSION_TIMER") == "1":
        try:
            from session_handling import mark_inactive_sessions

            count = mark_inactive_sessions(
                ttl=SESSION_TTL_SECONDS
            )

            logging.info(
                "Managed session check complete. New timeouts: %s",
                count,
            )

        except Exception:
            logging.exception(
                "Managed session inactivity check failed"
            )

        time.sleep(CHECK_INTERVAL_SECONDS)