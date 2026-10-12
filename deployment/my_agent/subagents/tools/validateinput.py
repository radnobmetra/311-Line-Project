from google.adk.tools.tool_context import ToolContext

#import safety and security functions 

from .emergency_check import emergency_check
from .user_request_tracking import invalid_request_limit_reached

#task 139: move user_mal_input and check_input_len to new files
from .user_mal_input import user_mal_input
from .check_input_len import check_input_len

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