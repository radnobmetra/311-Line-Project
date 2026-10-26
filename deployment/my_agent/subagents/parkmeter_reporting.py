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

from my_agent.subagents.tools import parking_meter_type
from ..config import MODEL, PARKING_METER_REPORTER
from .tools.submit_parkmeter_report import submit_report
from .tools.parking_meter_type import process_parking_meter_type

parkmeter_agent = LlmAgent (
    model = MODEL,
    name="ParkingMeterAgent",
    description= "Receives the status of a parking meter, gets location and identifier for a parking meter, verifies it is within city limits, and reports it.",
    instruction=PARKING_METER_REPORTER,
    tools=[submit_report, process_parking_meter_type],
)