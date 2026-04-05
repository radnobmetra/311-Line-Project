from google.adk.agents import LlmAgent
from ..config import MODEL, TICKETSTATUS_INSTRUCTION
from .tools.ticket_lookup import get_ticket_status

ticketstatus_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusAgent",
    description="Finds and returns ticket status updates.",
    instruction=TICKETSTATUS_INSTRUCTION,
    tools=[get_ticket_status],
    output_key="ticketstatus",
)
