from google.adk.agents import LlmAgent
from ..config import MODEL
from .tools.database import conversation_record


end_conversation = LlmAgent(
    model=MODEL,
    name="EndConversationAgent",
    description="Gracefully end conversation.",
    instruction="""
    If the user doesn't have any more questions, make sure to do these things:
    - First you must call the 'conversation_record' tool. Regardless of if the user is satisfied, hostile, or hits an invalid request limit, calling 'conversation_record' needs to be done before anything below it.
    - End the conversation politely by confirming. For example, say something like: 'Great!' or 'You're welcome!' if they say thank you. DON'T DOUBLE CONFIRM.
    - Finish by adding 'Thank you for contacting 311 service center.'.""",
    tools=[
        conversation_record
    ],
)
