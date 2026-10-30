from pathlib import Path
import os
from dotenv import load_dotenv
import time

# load root .env first, then fallback to subfolder path
load_dotenv()
load_dotenv('./my_agent/.env')


# handles EVEN MORE issues with cloud account shenanigans
PROJECT_ID = os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("AGENT_RUNTIME_LOCATION") or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-west1")


PROJECT_DIR = Path(__file__).resolve().parent

credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_path:
    credentials_file = Path(credentials_path).expanduser()

    if not credentials_file.is_absolute():
        credentials_file = PROJECT_DIR / credentials_file

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
        credentials_file.resolve()
    )




import agentplatform
import google.auth
import uuid
from datetime import datetime, timedelta, timezone





os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "TRUE"
client = agentplatform.Client(
  project=PROJECT_ID,
  location=LOCATION
)




adc_credentials, _ = google.auth.default(
	scopes = ["https://www.googleapis.com/auth/cloud-platform"]	         
)
print("ADC Service Account: ", getattr(adc_credentials, "Service account email", None))


def get_update_time(session):
    updated = session.update_time

    if isinstance(updated, str):
        updated = datetime.fromisoformat(
            updated.replace("Z", "+00:00")
        )

    if updated.tzinfo is None:
        updated = updated.replace(
            tzinfo=timezone.utc
        )

    return updated

def create_update_agent_session(
    user_Number: str,ttl: int,source: str) -> str:
    """
    Reuse the user's most recently updated session if it
    has been active within ttl seconds.
	Otherwise, create a new session.
    
    Inputs:
		user_Number (str):  usersPhone Number / Identifier
		ttl (int): Time-to-live in seconds
		source (str): adding onto user id to mark identifier
    
    Returns:
		str: Google-generated session ID
    """

    possible_sessions = list_users_sessions(
        user_Number=user_Number,
        source=source
    )

    if not possible_sessions:
        return create_session(
            user_Number=user_Number,
            source=source
        )



    latest_session = max(
        possible_sessions,
        key=get_update_time
    )

    last_updated = get_update_time(latest_session)

    elapsed = (
        datetime.now(timezone.utc) - last_updated
    ).total_seconds()

    old_session_id = latest_session.name.rsplit("/", 1)[-1]
    # Never reopen a timed-out or evaluated session.
    events = list_events(old_session_id)

    if any(
        event.author in (
            "session_timeout",
            "eval_author",
            "evaluation_skipped"
        )
        for event in events
    ):
        return create_session(
            user_Number=user_Number,
            source=source
        )


    if elapsed < ttl:
        return old_session_id

    mark_session_resolved(old_session_id)

    return create_session(
        user_Number=user_Number,
        source=source
    )


def add_custom_event(author:str, custom_data:dict, session_ID:int):
		
	"""
	Appends a message as an event to the attached session with custom author

	Args:

	Inputs: 
		author (str): author of the message for tracking
		custom_data (str): custom data to be appended 
		session_ID (int): session to add the event true
	Returns:
		True if completed
	"""

	### Appending the users message
	client.sessions.events.append(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"] + "/sessions/" + str(session_ID), 
		invocation_id = str(uuid.uuid4()),
		timestamp = datetime.now(tz=timezone.utc),
		author=author,
		config={
			"content": {
				"role": "user",
				"parts": [{"text": custom_data}]
				},
			},
	)
	return True

	


def create_session(user_Number: str, source: str) -> str:
    """
    Creates a session with the user ID.
    
    Inputs:
		user_Number (str): Users ID, used in format <user_Number>-<source>
		source (str): Source of session creation

    Returns:
        str: Google-generated session ID
    """

    user_ID = f"{user_Number}-{source}"

    operation = client.sessions.create(
        name=(
            "reasoningEngines/"
            + os.environ["SESSION_AGENT_ENGINE_ID"]
        ),
        user_id=user_ID,
        config={"wait_for_completion": True}
    )

    # Get the actual session from the completed operation.
    session = operation.response

    if session is None or not session.name:
        raise RuntimeError(
            "Session creation did not return a completed session. "
            f"Operation: {operation.name}, "
            f"Error: {operation.error}"
        )

    # Extract the session ID, not the operation ID.
    session_ID = session.name.rsplit("/", 1)[-1]

    return session_ID



def list_users_sessions(user_Number:str, source:str):
	"""
	Returns a list of sessions from a given user ID

	Args:

	Inputs: 
		user_Number(str): Users ID, used in format <user_Number>-<source>
		source(str): Source of session creation
	Returns:
		sessions(sessions[]): List of sessions
	"""
	filter_query = "user_id=" + user_Number + "-" + source

	return list_filtered_sessions(filter_query)
	

	
def list_events(session_ID:int):
	"""
	Lists all events for a given session_ID

	Args:

	Inputs: 
		session_ID(int) ID that the events are from
	Returns:
		events(list of events): List of events
	"""

	events = []
	for session_event in client.sessions.events.list(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"] + "/sessions/" + str(session_ID),
	):
		events.append(session_event)
	return events



def list_sessions():
	"""
	Lists of all sessions

	Args:

	Inputs: 
		None
	Returns:
		List of sesssions
	"""
	
	sessions = []
	for session in client.sessions.list(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"],
		#config={"filter": "user_id=managed-runtime-test-ad3df20d" }
	):
		sessions.append(session)
	return sessions

	

def delete_session(session_ID:int):
	"""
	deletes a session

	Args:
		
	Inputs: 
		session_ID(int): ID to be deleted
	Returns:
		True if deleted
	"""

	client.sessions.delete(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"] + "/sessions/" + str(session_ID),
	)
	return True



def _session_name(session_ID: str) -> str:
    """Build the Google session resource name."""
    return (
        f"reasoningEngines/{os.environ['SESSION_AGENT_ENGINE_ID']}"
        f"/sessions/{session_ID}"
    )



def add_user_message(
    user_Message: str,
    session_ID: str,
    invocation_id: str | None = None,
    return_invocation_id: bool = False
) -> bool | str:
    """
    Append a user message to a session.
    
    Inputs:
		user_Message (str): The message to append.
		session_ID (str): The session to append the message to.
		invocation_id (str | None): Optional invocation ID to link this message to a specific agent response.

    Returns:
		True by default if completed
    	Optionally returns the invocation ID.
    """

    if invocation_id is None:
        invocation_id = str(uuid.uuid4())

    client.sessions.events.append(
        name=_session_name(session_ID),
        invocation_id=invocation_id,
        timestamp=datetime.now(tz=timezone.utc),
        author="user",
        config={
            "content": {
                "role": "user",
                "parts": [{"text": user_Message}]
            }
        }
    )

    if return_invocation_id:
        return invocation_id

    return True



def list_events(session_ID: str):
    """Return all session events in chronological order."""
    events = list(
        client.sessions.events.list(
            name=_session_name(session_ID)
        )
    )

    return sorted(events, key=lambda event: event.timestamp)


def get_event_id(event) -> str | None:
    """
    Extract the ID of a saved session event.

    ADK events may expose raw_event.id.
    Regular saved events expose a resource name.
    """
    raw_event = getattr(event, "raw_event", None)

    if isinstance(raw_event, dict) and raw_event.get("id"):
        return str(raw_event["id"])

    event_name = getattr(event, "name", None)

    if event_name and "/events/" in event_name:
        return event_name.rsplit("/", 1)[-1]

    return None


def get_agent_response_event(
    session_ID: str,
    event_ID: str
):
    """
    Retrieve a particular saved agent response.
    Returns None when no matching response exists.
    """
    for event in list_events(session_ID):
        if (
            event.author == "agent"
            and get_event_id(event) == str(event_ID)
        ):
            return event

    return None


def add_agent_message(
    agent_Message: str,
    session_ID: str,
    invocation_id: str
) -> str:
    """
    Save an agent response and return its event ID.
    The invocation ID must match the user message
    that triggered this response.
    """
    client.sessions.events.append(
        name=_session_name(session_ID),
        invocation_id=invocation_id,
        timestamp=datetime.now(tz=timezone.utc),
        author="agent",
        config={
            "content": {
                "role": "model",
                "parts": [{"text": agent_Message}]
            }
        }
    )

    # append() does not directly return the saved event ID,
    # so retrieve the event from the session afterward.
    matches = []

    for event in list_events(session_ID):
        if event.author != "agent":
            continue

        if event.invocation_id != invocation_id:
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        text = "".join(
            part.text or ""
            for part in parts
            if getattr(part, "text", None) is not None
        )

        if text == agent_Message:
            matches.append(event)

    if not matches:
        raise RuntimeError(
            "Agent message was appended, but its event "
            "could not be retrieved."
        )

    latest_event = matches[-1]
    event_id = get_event_id(latest_event)

    if not event_id:
        raise RuntimeError(
            "Saved agent event has no accessible event ID."
        )

    return event_id

def mark_session_resolved(session_ID: str) -> bool:
    """
    Appends a state update event to mark a time over session as resolved.
    """
    client.sessions.events.append(
        name=_session_name(session_ID),
        invocation_id=str(uuid.uuid4()),
        timestamp=datetime.now(tz=timezone.utc),
        author="system",
        config={
            "actions": {
                "state_delta": {
                    "status": "resolved",
                    "outcome_label": "session timeout",
                }
            },
            "content": {
                "role": "model",
                "parts": [{"text": "Session resolved due to timeout."}]
            }
        }
    )
    return True


def get_session(session_ID: str):
    """Retrieve a session resource by its ID."""
    return client.sessions.get(
        name=_session_name(session_ID)
    )

def list_filtered_sessions(filter_query:str):
    """
     
    """
    sessions = client.sessions.list(
	name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"],
	config={"filter": filter_query}
	)
    return list(sessions)
     



def mark_inactive_sessions(ttl: int):
    import hashlib
    import logging
    from evaluation_handling import evaluate_completed_session

    sample_rate = float(
        os.environ.get("EVALUATION_SAMPLE_RATE", "0.10")
    )

    if not 0 <= sample_rate <= 1:
        raise ValueError("EVALUATION_SAMPLE_RATE must be between 0 and 1")

    inactive_sessions = 0

    for session in list_sessions():
        session_id = session.name.rsplit("/", 1)[-1]
        events = list_events(session_id)

        # Skip completely empty sessions.
        if not events:
            continue

        authors = {event.author for event in events}

        # Already evaluated or deliberately excluded.
        if "eval_author" in authors or "evaluation_skipped" in authors:
            continue

        already_timed_out = "session_timeout" in authors

        if not already_timed_out:
            inactive_time = (
                datetime.now(timezone.utc) - get_update_time(session)
            ).total_seconds()

            if inactive_time < ttl:
                continue

            add_custom_event(
                "session_timeout",
                "closed: timeout",
                session_id
            )
            inactive_sessions += 1

        # Don't evaluate conversations without user messages.
        if "user" not in authors:
            add_custom_event(
                "evaluation_skipped",
                "no_user_messages",
                session_id
            )
            continue

        # Deterministically select approximately 10%.
        hash_value = int.from_bytes(
            hashlib.sha256(session_id.encode()).digest()[:8],
            "big"
        )
        selected = hash_value / (1 << 64) < sample_rate

        if not selected:
            add_custom_event(
                "evaluation_skipped",
                "not_selected_for_sampling",
                session_id
            )
            continue

        # Evaluate selected sessions.
        result = evaluate_completed_session(session_id)

        if result is None:
            logging.error(
                "Evaluation failed for session %s",
                session_id
            )

    return inactive_sessions
