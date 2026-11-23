
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

streetlight_tool = importlib.import_module(
    "my_agent.subagents.tools.verify_streetlight"
)

from my_agent.subagents.streetlight_reporting import streetlight_reporting_agent


def test_valid_streetlight_number(monkeypatch):
    # Simulate ArcGIS finding a matching streetlight.
    response = Mock()
    response.json.return_value = {
        "features": [{
            "attributes": {
                "ASSET_ID": "SL-1234",
                "POLE_TYPE": "Standard",
                "WATTAGE": 100
            }
        }]
    }

    get = Mock(return_value=response)
    monkeypatch.setattr(streetlight_tool.requests, "get", get)

    result = json.loads(
        streetlight_tool.verify_streetlight(
            "SL-1234", SimpleNamespace(state={})
        )
    )

    assert result["verified"] is True
    assert result["details"]["asset_id"] == "SL-1234"

    # Confirm the correct pole number was queried.
    assert "ASSET_ID='SL-1234'" in get.call_args.kwargs["params"]["where"]

    print("\n--- VALID STREETLIGHT ---")
    print("Input: SL-1234")
    print(f"Verification result: {result['verified']}")
    print(f"Streetlight details: {result['details']}")


def test_invalid_streetlight_number(monkeypatch):
    # Simulate ArcGIS finding no matching streetlight.
    response = Mock()
    response.json.return_value = {"features": []}

    monkeypatch.setattr(
        streetlight_tool.requests,
        "get",
        Mock(return_value=response)
    )

    result = json.loads(
        streetlight_tool.verify_streetlight(
            "NOT-A-REAL-POLE", SimpleNamespace(state={})
        )
    )

    assert result["verified"] is False
    assert "No streetlight found" in result["message"]

    print("\n--- INVALID STREETLIGHT ---")
    print("Input: NOT-A-REAL-POLE")
    print(f"Verification result: {result['verified']}")
    print(f"Message: {result['message']}")


def test_streetlight_agent_uses_verification_tool():
    assert (
        streetlight_tool.verify_streetlight
        in streetlight_reporting_agent.tools
    )
