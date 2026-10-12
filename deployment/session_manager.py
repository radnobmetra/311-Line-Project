from google.adk.sessions import InMemorySessionService

app_name = "my_agent"

session_service = InMemorySessionService()

def session_service_builder():
    return session_service