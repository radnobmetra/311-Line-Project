from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent, InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import AsyncGenerator, Optional  
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse 
from ..config import MODEL, TICKETSTATUS_INSTRUCTION
from .tools.ticket_lookup import get_ticket_status
from .tools.ticket_validator import validate_ticket

def save_user_question(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    user_question = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if getattr(content, "role", None) == "user" and getattr(content, "parts", None):
                for part in content.parts:
                    text = getattr(part, "text", None)
                    if text:
                        user_question = text
                        break
            if user_question:
                break

    callback_context.state["user_question"] = user_question
    return None

ticketstatus_draft_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusAgent",
    description="Finds and returns ticket status updates.",
    instruction=TICKETSTATUS_INSTRUCTION,
    tools=[get_ticket_status, validate_ticket],
    before_model_callback=save_user_question,
    output_key="ticketstatus",
)


ticketstatus_reviewer_agent = LlmAgent(
    model=MODEL,
    name="TicketStatusReviewerAgent",
    description="Checks whether the ticket status answer is acceptable.",
    instruction='''
You are a strict reviewer for ticket lookups.

Original user question:
{user_question}

Draft answer:
{ticketstatus}

Classify the draft into exactly one label:

- pass
    Use if the draft correctly answers the user's ticket question
    and includes ticket information for a specific ticket.

- needs_ticket_number
    Use if the draft correctly asks the user to provide a ticket number.

- multiple_ticket_numbers
    Use if the draft correctly asks the user which ticket number they mean.

- ticket_not_found
    Use if the draft says the ticket does not exist, no information was found,
    or no ticket was found for the provided number.

- retrieval_error
    Use if the draft says there was an error retrieving ticket data or the answer
    is otherwise broken, unsupported, or unusable.

Be strict.
Return exactly one label and nothing else:
pass
needs_ticket_number
multiple_ticket_numbers
ticket_not_found
retrieval_error
''',
    output_key="ticketstatus_review",
)

class ValidateTicketStatus(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("ticketstatus_review", "retrieval_error")
        answer = ctx.session.state.get("ticketstatus", "").strip()

        if status in {
            "pass",
            "needs_ticket_number",
            "multiple_ticket_numbers",
            "ticket_not_found",
        }:
            final_answer = answer
        else:  # retrieval_error
            final_answer = (
                "There was an error retrieving the ticket information. "
                "Please try again or contact the 311 call line for assistance."
            )

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_answer)])
        )

validate_ticketstatus_agent = ValidateTicketStatus(
    name="ValidateTicketStatusAgent",
    description="Returns the ticket answer only if it passed review.",
)

ticketstatus_agent = SequentialAgent(
    name="TicketStatusWorkflowAgent",
    sub_agents=[
        ticketstatus_draft_agent,
        ticketstatus_reviewer_agent,
        validate_ticketstatus_agent,
    ],
)