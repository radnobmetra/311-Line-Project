from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent, InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import AsyncGenerator, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any
from google.adk.models import LlmRequest, LlmResponse
from ..config import MODEL, POTHOLE_REPORTER
from .tools.submit_pothole_report import submit_report
import google.genai.types as types
from typing import List


async def is_image_uploaded(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmRequest | None:
    for content in llm_request.contents:
        if not content.parts:
            continue

        images = []
        for idx, part in enumerate(content.parts):
            if part.inline_data:
                await image_into_artifact(part, callback_context)

async def image_into_artifact(
        part: Part, callback_content: CallbackContext
) -> List[Part]:
    """Takes the users input and converts the image into an artifact."""

    image_data = part.inline_data.data
    """Saves generated PDF report bytes as an artifact."""
    report_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_data
            )
        )
    filename = "user_image"
    try:
        savedfile = await callback_content.save_artifact(filename=filename, artifact=report_artifact)
        print("File saved")
    except ValueError as e:
        print("Error occured: {e}")
    except Exception as e:
        print("More Fun Error Occured: {e}")
        













pothole_report_draft_agent = LlmAgent(
        model = MODEL,
        name ="PotholeReportingAgent",
        description = "Gets location for a pothole and an image, verifies it is within city limits and reports it.",
        instruction = POTHOLE_REPORTER,
        before_model_callback=is_image_uploaded,
        tools=[submit_report],
    )



