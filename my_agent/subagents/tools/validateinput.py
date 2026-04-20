from google.adk.tools.tool_context import ToolContext

#import safety and security functions 

from .emergency_check import emergency_check
from .user_request_tracking import invalid_request_limit_reached

#task 139: move user_mal_input and check_input_len to new files
#from <new_filename> import user_mal_input
#from <new_filename> import check_input_len

#to do: delete user_mal_input and check_input_len and import them from new files once story 139 is done
#they are copy and pasted here to avoid circular import error, which occurs when they are imported from overseer.py

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

def validateInput (tool_context: ToolContext) -> bool:
    """
    Checks if the user's input is valid.

    Args:
        tool_context(ToolContext): The tool context.

    Returns:
        bool: True if the user's input is valid, False if the user's input is invalid.
    """

    request_is_valid = True

    #get user input from ToolContext
    user_input = "N/A"
    if tool_context.session.events:
        for event in reversed(tool_context.session.events):
            if event.author == 'user':
                user_input = event.content.parts[0].text
                break

    #run security functions

    if invalid_request_limit_reached(tool_context):
        request_is_valid = False

    elif user_mal_input(user_input):
        request_is_valid = False
    
    elif emergency_check(user_input) == "Emergency Alert":
        request_is_valid = False

    elif check_input_len(user_input) == False:
        request_is_valid = False

    return request_is_valid