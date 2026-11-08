from google.adk.agents import LlmAgent
from .session_reviewer import session_reviewer
from ..config import MODEL, END_CONVERSATION_INSTRUCTION
from .tools.database import conversation_record

end_conversation = LlmAgent(
    model=MODEL,
    name="EndConversationAgent",
    description="Gracefully end conversation.",
    instruction=END_CONVERSATION_INSTRUCTION,
    sub_agents = [session_reviewer],
    tools=[
        conversation_record
    ],
)