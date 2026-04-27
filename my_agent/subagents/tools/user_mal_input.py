import json
import re

def user_mal_input(user_input: str) -> bool:
    """
    Checks if the user's input is malicious.

    Args:
        user_input (str): The user input to check.

    Returns:
        bool: True if the user's input is found to be malicious, False otherwise.
    """
    # Set list "mal_keywords" to the contents of the emergency_cases.json file
    with open('emergency_cases.json', 'r') as file:
        mal_keywords = json.load(file)


    #maybe we will make it so we check context here?
    # Only uses the malicious word section 
    # might need to change to phrases instead of words
    mal_section = mal_keywords['malicious_key']
    # Checks each keyword in the list against the user input.
    for keyword in mal_section:
        x=re.search(keyword,user_input.lower())

        if x: 
            # Returns True if any malicious keyword is found in the user input.
            return True
    # Returns False if no detections are made.
    return False