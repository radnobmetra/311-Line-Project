import time
import json
import os
import asyncio
from my_agent.subagents.end_conversation import end_conversation 
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

#hurryup checks if user sent a message, timesup is the timer in seconds
HURRY_UP = "useronline.json"
TIMES_UP = 30*60

def run_loop():
    while True:
        if os.path.exists(HURRY_UP):
            with open(HURRY_UP, "r") as file:
                try:
                    sessions = json.load(file)
                except json.JSONDecodeError:
                    sessions = {}

            current_time = time.time()
            active_sessions = {}
            db_updated = False

            for user_id, data in sessions.items():
                if current_time - data.get("last_active", 0) >= TIMES_UP:
                    print(f"\nSession timed out! Logging transcript...")
                    
                    transcript = data.get("transcript", "")
                    #doesnt rly work but it does?
                    prompt_text = f"System: The user is inactive. Log this transcript using your tool, say goodbye, and run the session_reviewer. Transcript:\n{transcript}" 
                    
                    app_name = "TimeoutMonitor"
                    sess_id = f"timeout_{user_id}"
                    session_service = InMemorySessionService()
                    asyncio.run(session_service.create_session(app_name=app_name, user_id=user_id, session_id=sess_id))
                    runner = Runner(agent=end_conversation, app_name=app_name, session_service=session_service)
                    content = types.Content(role="user", parts=[types.Part(text=prompt_text)])
                    
                    # bugs agent to run and captures it
                    events = runner.run(user_id=user_id, session_id=sess_id, new_message=content)
                    for event in events:
                        pass
                    print("Logged!")
                    
                    
                    # will likely come back to edit this heavily when sms drops
                    # web server is rly weird with this stuff, sms should be more flexible, i hope..


                    db_updated = True
                else:
                    active_sessions[user_id] = data

            if db_updated:
                with open(HURRY_UP, "w") as file:
                    json.dump(active_sessions, file, indent=4)
        #efficency  
        time.sleep(5)