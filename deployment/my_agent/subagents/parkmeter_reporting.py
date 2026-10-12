from google.adk.agents import LlmAgent, BaseAgent, InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import AsyncGenerator, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
from google.adk.models import LlmRequest, LlmResponse
from ..config import MODEL, PARKING_METER_REPORTER
from .tools.submit_parkmeter_report import submit_report

parkmeter_agent = LlmAgent (
    model = MODEL,
    name="ParkingMeterAgent",
    description= "Gets location and identifier for a parking meter, verifies it is within city limits, and reports it.",
    instruction=PARKING_METER_REPORTER,
    tools=[submit_report],
)