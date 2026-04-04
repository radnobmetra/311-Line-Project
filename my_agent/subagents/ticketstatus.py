from google.adk.agents import LlmAgent
from ..config import MODEL, TICKETSTATUS_INSTRUCTION
from .tools.ticket_search import search_tickets


ticketstatus_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusAgent",
    description="Finds and returns ticket status updates.",
    instruction=TICKETSTATUS_INSTRUCTION,
    tools=[search_tickets],
    output_key="ticketstatus",
)
