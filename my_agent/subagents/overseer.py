from google.adk.agents import LlmAgent
from ..config import MODEL, OVERSEER_INSTRUCTION
from qa import qa_agent
from ticketstatus import ticketstatus_agent

overseer_agent = LlmAgent(
    model=MODEL,
    name="OverseerAgent",
    description="Routes user requests to the correct specialist and returns a single final response.",
    instruction=OVERSEER_INSTRUCTION,
    sub_agents=[qa_agent, ticketstatus_agent],
)
