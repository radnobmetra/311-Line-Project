from google.adk.agents import LlmAgent
from ..config import MODEL, STREETLIGHT_REPORTER
from .tools.submit_report import submit_report
from .tools.address_to_coords import get_coordinates
from .tools.within_city_limits import verify_address
from .pothole_reporting import is_image_uploaded
from .tools.verify_streetlight import verify_streetlight

streetlight_reporting_agent = LlmAgent(
    model=MODEL,
    name="StreetlightReportingAgent",
    description="Gets location and pole number for a broken streetlight, accepts photos, verifies city limits, and reports it.",
    instruction=STREETLIGHT_REPORTER,
    before_model_callback=is_image_uploaded,
    tools=[get_coordinates, verify_address, submit_report, verify_streetlight],
)