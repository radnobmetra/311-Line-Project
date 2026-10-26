from enum import Enum
from typing import Annotated
from pydantic import BaseModel, Field


def process_parking_meter_type(agent_category: str) -> str:
    """
    Determines the type of parking meter issue based on the user's input.

    Args:
        agent_category (str): The category of the parking meter issue chosen by the parking meter agent.

    Returns:
        str: A string indicating what to do for each category.
    """
    input = agent_category.lower()
    
    if "coin" in input or "card" in input:
        return "Meter payment required with card or payment app"
    elif "payment" in input:
        return "Inoperable meter. Report meter to Sacramento City 311. Use the PKGS number at the bottom of the screen. Move to another space if available."
    elif "screen" in input:
        return "Inoperable meter. Report meter to Sacramento City 311. Report the digits on the green Parkmobile app sticker as meter number. Move to another space if available."
    else:
        return "Other issue. Meter inoperable."