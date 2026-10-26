import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google.adk.tools.tool_context import ToolContext
from my_agent.subagents.tools.submit_report import submit_report

# mock ToolContext to capture state changes
class MockToolContext(ToolContext):
    def __init__(self):
        self._mock_state = {}

    @property
    def state(self):
        return self._mock_state

    @property
    def session(self):
        return None

    @property
    def store(self):
        return None

def test_submit_report_empty_location_sets_error_state():
    mock_context = MockToolContext()
    
    response = submit_report(
        report_type="pothole", 
        location="", 
        tool_context=mock_context
    )
    
    assert "Error" in response
    assert "outcome_label" in mock_context.state
    assert mock_context.state["outcome_label"] == "No valid address provided for submission."

def test_submit_report_simulator_failure_sets_error_state(monkeypatch):
    mock_context = MockToolContext()
    
    import my_agent.subagents.tools.submit_report as sr
    monkeypatch.setattr(sr, "errorMode", True)
    
    response = submit_report(
        report_type="streetlight", 
        location="123 Main St", 
        tool_context=mock_context
    )
    
    assert "Error" in response
    assert "outcome_label" in mock_context.state
    assert mock_context.state["outcome_label"] == "Submission simulator failure."