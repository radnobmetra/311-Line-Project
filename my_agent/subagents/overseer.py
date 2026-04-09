from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from ..config import MODEL, OVERSEER_INSTRUCTION
from .qa import qa_agent
from .ticketstatus import ticketstatus_agent
from .greeting_agent import greeting_agent

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

def check_input_len(user_input: str) -> bool:
    """
    Counts the number of chars in the user's input and ensures that 70% of the input is made up of ASCII characters.
    
    Args:
        user_input (str): The user input to check.

    Returns:
        bool: True if 70% or more of the characters in the user's input are ASCII, False otherwise.
    """
    counter = 0
    # Progresses through each character in the user input.
    for char in user_input:
        # ord() returns the Unicode code point of the character.
        if ord(char) < 128:
            counter = counter + 1
    # Returns True if the user's input is at least 70% ASCII characters.
    if counter / len(user_input) >= 0.7:
        return True
    # Returns False if otherwise.
    return False

overseer_agent = LlmAgent(
    model=MODEL,
    name="OverseerAgent",
    description="Routes user requests to the correct specialist and returns a single final response.",
    instruction=OVERSEER_INSTRUCTION,
    sub_agents=[qa_agent, ticketstatus_agent],
    tools=[AgentTool(agent=greeting_agent), user_mal_input, check_input_len],
)
