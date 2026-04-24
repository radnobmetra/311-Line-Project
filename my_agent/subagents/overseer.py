from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from ..config import MODEL, OVERSEER_INSTRUCTION
from .qa import qa_agent
from .ticketstatus import ticketstatus_agent
from .greeting_agent import greeting_agent
from .end_conversation import end_conversation
from .tools.user_request_tracking import update_num_invalid_requests
from .tools.validateinput import validateInput

overseer_agent = LlmAgent(
    model=MODEL,
    name="OverseerAgent",
    description="Routes user requests to the correct specialist and returns a single final response.",
    instruction=OVERSEER_INSTRUCTION,
    sub_agents=[qa_agent, ticketstatus_agent, end_conversation],
    tools=[
        AgentTool(agent=greeting_agent),
        validateInput,
        update_num_invalid_requests,
    ],
)
