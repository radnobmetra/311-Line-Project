from google.adk.agents import LlmAgent
from ..config import MODEL, TICKETSTATUS_INSTRUCTION
from .tools.ticket_lookup import get_ticket_status
from .tools.ticket_validator import validate_ticket

ticketstatus_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusAgent",
    description="Finds and returns ticket status updates.",
    instruction=TICKETSTATUS_INSTRUCTION,
    tools=[get_ticket_status, validate_ticket],
    output_key="ticketstatus",
)
