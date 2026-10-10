from pathlib import Path
import os
from dotenv import load_dotenv
import time

load_dotenv('./my_agent/.env')

## Handles issues with cloud account shenanigans
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
LOCATION = os.environ["AGENT_RUNTIME_LOCATION"]

PROJECT_DIR = Path(__file__).resolve()
# GOOGLE_CREDENTAILS IN "./sa-key.json" - ENV File

raw_credentials = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
CREDENTIALS_FILE = (
	raw_credentials.resolve()
	if raw_credentials.is_absolute()
	else (PROJECT_DIR/raw_credentials.resolve())
)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(CREDENTIALS_FILE)



import agentplatform
import google.auth
import uuid
from datetime import datetime, timedelta, timezone



client = agentplatform.Client(
  project=PROJECT_ID,
  location=LOCATION
)




adc_credentials, _ = google.auth.default(
	scopes = ["https://www.googleapis.com/auth/cloud-platform"]	         
)
print("ADC Service Account: ", getattr(adc_credentials, "Service account email", None))


	
def create_update_agent_session(user_Number:str, ttl:int, source:str):
	"""
	This function returns a session ID based upon the given user_number. 
	If the most recent session is null or older than ttl, a new session is created.

	Args:

	Inputs: 
		user_Number (int): usersPhone Number / Identifier
		ttl (str): time to live in seconds, if the previous session is older than the ttl then a new one is created
		source (str): adding onto user id to mark identifier

	Returns:
		session_id(str) ID of the session to use
	"""
	

	possible_sessions:list = list_users_sessions(user_Number=user_Number, source=source)
	

	if len(possible_sessions) == 0:
		## If no sessions exist for this user, make a new session since we can garuntee there isnt one.
		new_session = create_session(user_Number=user_Number, source=source)
	else:
		latest_session = possible_sessions[0]
		update_age = latest_session.update_time
		update_time_str = str(update_age)
		clipped_time_str = update_time_str[0:-13]
		
		#Y = 4 digit year, %m = zero padded month, %d = 0 padded day, %H = 0 padded hour, %M = 0 Padded minute, %S = 0 padded second
		update_time_localized = datetime.strptime(clipped_time_str, "%Y-%m-%d %H:%M:%S")
		now_time = datetime.now(tz=timezone.utc)
		now_time_str = str(now_time)

		# Removing junk data
		now_time_str = now_time_str[0:-13]
		now_time_utc = datetime.strptime(now_time_str, "%Y-%m-%d %H:%M:%S")


		# Subtracting current time from localized since now time is higher value
		time_gap = now_time_utc - update_time_localized
		time_gap_seconds = time_gap.total_seconds()
		if time_gap_seconds < ttl:
			# Sesssion Name contains the ID as the last in the filepath
			latest_session_id = str(latest_session.name).split("/")[-1]
			return latest_session_id
		else:

			new_session = create_session(user_Number=user_Number, source=source)
			return new_session

		

def add_user_message(user_Message:str, session_ID:int):
	"""
		Appends a message as an event to the attached session as the user

	Args:

	Inputs: 
		user_Message (str): users message to be appended
		session_ID (int): session to add the event true
	Returns:
		True if completed
	"""

	### Appending the users message
	client.sessions.events.append(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"] + "/sessions/" + str(session_ID), 
		invocation_id = str(uuid.uuid4()),
		timestamp = datetime.now(tz=timezone.utc),
		author="user",
		config={
			"content": {
				"role": "user",
				"parts": [{"text": user_Message}]

			},
		},
	)
	return True

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

	

def create_session(user_Number:str, source:str):
	"""
	Creates a session with the user id

	Args:

	Inputs: 
		user_Number(str): Users ID, used in format <user_Number>-<source>
		source(str): Source of session creation
	Returns:
		True if completed
	"""

	# Format is <Phone-Number>-<source>
	user_ID = user_Number + "-" + source
	session = client.sessions.create(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"],
		user_id = user_ID
	)
	# Sesssion Name contains the ID as the last in the filepath
	session_ID = str(session.name).split("/")[-3]
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
	
	sessions = client.sessions.list(
		name = "reasoningEngines/" +os.environ["SESSION_AGENT_ENGINE_ID"],
		config={"filter": filter_query}
	)
	return sessions
	
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
		config={"filter": "user_id=managed-runtime-test-ad3df20d" }
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

