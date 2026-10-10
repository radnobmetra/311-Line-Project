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

