import pytest
import os
from pathlib import Path
import sys
sys.path.insert(1, "..\\311-Line-Project")

import session_handling

def test_creating_sessions():
	# Make new session in order to verify creation
	testNum = "916-555-5555"
	source = "pytest"

	# 0 TTL in order to force new session
	newID = session_handling.create_update_agent_session(user_Number=testNum, ttl=0, source=source)


	secondID = session_handling.create_update_agent_session(user_Number=testNum, ttl=50000, source=source)
	assert newID == secondID

def test_list_sessions():
	testNum = "916-555-5555"
	source = "pytest"

	sessions = session_handling.list_sessions()

	assert len(sessions) > 0


def test_add_user_message():
	testNum = "916-555-5555"
	source = "pytest"
	testID = 735261567435669504
	testMessage = "TEST1, Pytest"
	
	assert session_handling.add_user_message(testMessage, testID) == True

def test_add_custom_event():
	testID = 735261567435669504
	author = "pytest"
	custom_data = "TestAgent Message"
	
	
	assert session_handling.add_custom_event(author, custom_data, testID) == True

def test_list_users_sessions():
	testNum = "916-555-5555"
	author = "pytest"

	sessions = session_handling.list_users_sessions(testNum, author)
	print(sessions)
	assert len(sessions) > 0

def test_list_events():
	testNum = "916-555-5555"

	# Twilio as test event is twilio
	author = "twilio"
	testID = 735261567435669504

	events = session_handling.list_events(testID)
	print(events)
	assert len(events) > 0


def test_delete_sessions():
	testNum = "916-555-5555"
	author = "pytest"
	
	test_session = session_handling.create_session(testNum, author)

	output = session_handling.delete_session(test_session)
	assert output == True

def test_marking_inactive_sessions():
	ttl = 3.154e+7 # 1 Year in seconds

	session_count = session_handling.mark_inactive_sessions(ttl)
	assert session_count == 0
def test_timeout_marks_old_session_resolved():
	testNum = "916-555-5555"
	source = "pytest"

	old_id = session_handling.create_update_agent_session(
		user_Number=testNum, ttl=50000, source=source
	)

	# force a time over so old_id is marked resolved and a new session is created
	new_id = session_handling.create_update_agent_session(
		user_Number=testNum, ttl=0, source=source
	)

	assert old_id != new_id

	# verify state persistence on the old session's events and session state
	events = session_handling.list_events(old_id)
	assert len(events) > 0

	resolved_events = [
		e for e in events
		if getattr(e, "actions", None)
		and getattr(e.actions, "state_delta", None)
		and e.actions.state_delta.get("status") == "resolved"
	]
	assert len(resolved_events) > 0
	assert resolved_events[-1].actions.state_delta.get("outcome_label") == "session timeout"
