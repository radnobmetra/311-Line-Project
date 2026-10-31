import json
import re
from difflib import SequenceMatcher

phrases = [
    "bypass all security",
    "select from",
    "ignore warnings",
    "system override",
    "system error",
    "translate the following",
    "summarize the following"
    ]

def user_mal_input(user_input: str) -> str:
    """
    Checks if the user's input is malicious.

    Args:
        user_input (str): The user raw input to check.

    Returns:
        str: "REJECTED" if the user's input is found to be malicious, "ALLOWED" otherwise.
    """

    # Convert the user's input to lowercase for consistent checking.
    input = user_input.lower().strip()

    # CHECK 1: Input Length
    if len(input) > 150:
        print("Input too long, rejecting.")
        return "REJECTED"

    # CHECK 2: SQL Injection Patterns
    # Uses RegEx to check for SQL injection patterns.
    # Will match any SQL keywords at the beginning of the user input.
    if re.search(r'^(select|insert|update|delete|from)\s+\*.', input):
        print("SQL injection pattern detected, rejecting.")
        return "REJECTED"
    
    # Set list "mal_keywords" to the contents of the emergency_cases.json file
    with open('emergency_cases.json', 'r') as file:
        mal_keywords = json.load(file)

    # CHECK 3: Malicious Keywords from emergency_cases.json
    #maybe we will make it so we check context here?
    # Only uses the malicious word section 
    # might need to change to phrases instead of words
    mal_section = mal_keywords['malicious_key']
    # Checks each keyword in the list against the user input.
    for keyword in mal_section:
        if keyword in input:
            # Returns "REJECTED" if any malicious keyword is found in the user input.
            print(f"Malicious keyword '{keyword}' detected, rejecting.")
            return "REJECTED"
    
    # CHECK 4: Comparing user input to the malicious phrases at the top of the file
    input_list = input.split()
    # For each word in str1, except for the last two
    for x in range(len(input_list) - 2):
        # Creates a list of the current word and the 2 words ahead of it.
        # Ex: If x = 0, then input_list[0:3] grabs [0, 1, 2]
        chunks = input_list[x:x+3]
        # For every line in phrases.txt
        for y in phrases:
            phrase_clean = re.sub(r'[^\w\s]', '', y.lower()).split()
            # Compares the line in phrases to the chunk
            score = SequenceMatcher(None, phrase_clean, chunks).ratio()
            if score >= 0.4 and len(phrase_clean) >= 3:
                return "REJECTED"
            if score >= 0.8 and len(phrase_clean) == 2:
                return "REJECTED"

    # Returns "ALLOWED" if no detections are made.
    print("No malicious content detected, allowing.")
    return "ALLOWED"