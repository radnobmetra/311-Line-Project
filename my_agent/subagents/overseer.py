from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from ..config import MODEL, OVERSEER_INSTRUCTION
from .qa import qa_agent
from .ticketstatus import ticketstatus_agent
from .greeting_agent import greeting_agent
from .end_conversation import end_conversation
from .pothole_reporting import pothole_report_draft_agent
from .parkmeter_reporting import parkmeter_agent
from .tools.user_request_tracking import update_num_invalid_requests
from .tools.validateinput import validateInput

overseer_agent = LlmAgent(
    model=MODEL,
    name="OverseerAgent",
    description="Routes user requests to the correct specialist and returns a single final response.",
    instruction=OVERSEER_INSTRUCTION,
    sub_agents=[
        ticketstatus_agent, 
        end_conversation, 
        pothole_report_draft_agent, 
        parkmeter_agent
    ],
    tools=[
        qa_agent, 
        AgentTool(agent=greeting_agent),
        validateInput,
        update_num_invalid_requests,
    ],
)


