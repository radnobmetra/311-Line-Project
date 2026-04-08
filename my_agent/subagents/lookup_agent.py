from google.adk.agents import LlmAgent
from ..config import MODEL, LOOKUP_INSTRUCTION


greeting_agent = LlmAgent(
    model=MODEL,
    name="LookupAgent",
    description="Looks for specified info",
    instruction=LOOKUP_INSTRUCTION,
)