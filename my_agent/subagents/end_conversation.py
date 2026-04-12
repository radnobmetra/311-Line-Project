from google.adk.agents import LlmAgent
from ..config import MODEL


end_conversation = LlmAgent(
    model=MODEL,
    name="EndConversationAgent",
    description="Gracefully end conversation.",
    instruction="""""",
)
