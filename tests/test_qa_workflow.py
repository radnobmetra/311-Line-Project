#test that migration from sequential to workflow  exists and imports correctly
#use python -m pytest tests/test_qa_workflow.py -v

from google.adk import Workflow

from my_agent.subagents.qa import qa_agent
from my_agent import app


def test_qa_agent_is_workflow():
    assert isinstance(qa_agent, Workflow)


def test_app_loads_qa_workflow():
    assert app is not None
    assert app.root_agent is not None