from google.adk.agents import LlmAgent
from ..config import MODEL


end_conversation = LlmAgent(
    model=MODEL,
    name="EndConversationAgent",
    description="Gracefully end conversation.",
    instruction="""
    If the user doesn't have any more questions, make sure to do these things: 
    - End the conversation politely by confirming. For example, say something like: 'Great!' or 'You're welcome!' if they say thank you. DON'T DOUBLE CONFIRM.
    - Finish by adding 'Thank you for contacting 311 service center.'.""",
)
