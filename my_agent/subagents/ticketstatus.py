from google.adk.agents import LlmAgent
from ..config import MODEL, TICKETSTATUS_INSTRUCTION

ticketstatus_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusAgent",
    description="Finds and returns ticket status updates.",
    instruction=TICKETSTATUS_INSTRUCTION,
    output_key="ticketstatus",
)
