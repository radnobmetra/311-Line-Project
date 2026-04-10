from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from ..config import MODEL, OVERSEER_INSTRUCTION
from .qa import qa_agent
from .ticketstatus import ticketstatus_agent
from .greeting_agent import greeting_agent
from .tools.emergency_check import emergency_check

def user_mal_input(user_input: str) -> bool:
    """
    Checks if the user's input is malicious.
    
    Args:
        user_input (str): The user input to check.

    Returns:
        bool: True if the user's input is found to be malicious, False otherwise.
    """
    mal_keywords = ["firewall", "phish", "hack", "bypass", "sql inject", "ddos"]
    # Checks each keyword in the list against the user input.
    for keyword in mal_keywords:
        if keyword in user_input.lower():
            # Returns True if any malicious keyword is found in the user input.
            return True
    # Returns False if no detections are made.
    return False

overseer_agent = LlmAgent(
    model=MODEL,
    name="OverseerAgent",
    description="Routes user requests to the correct specialist and returns a single final response.",
    instruction=OVERSEER_INSTRUCTION,
    sub_agents=[qa_agent, ticketstatus_agent],
    tools=[AgentTool(agent=greeting_agent), emergency_check, user_mal_input],
)
