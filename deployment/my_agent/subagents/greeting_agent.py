from google.adk.agents import LlmAgent
from ..config import MODEL, GREETING_INSTRUCTION


greeting_agent = LlmAgent(
    model=MODEL,
    name="GreetingAgent",
    description="Greets user at the start of a new session.",
    instruction=GREETING_INSTRUCTION,
)
