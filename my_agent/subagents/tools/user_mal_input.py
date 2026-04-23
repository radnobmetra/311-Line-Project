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