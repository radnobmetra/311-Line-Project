import os

from google.adk.sessions import VertexAiSessionService
from vertexai.agent_engines import AdkApp

from my_agent.agent import root_agent


def session_service_builder():
    return VertexAiSessionService(
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location="us",
        agent_engine_id=os.environ["SESSION_AGENT_ENGINE_ID"],
    )


app = AdkApp(
    agent=root_agent,
    session_service_builder=session_service_builder,
)