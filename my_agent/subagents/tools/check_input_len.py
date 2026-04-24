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
        code = ord(char)
        if (code > 96 and code < 123) or (code > 64 and code <91) or (code > 47 and code < 58) or (code == 32):
            counter = counter + 1
    # Returns True if the user's input is at least 70% alphanumeric characters.
    if counter / len(user_input) >= 0.7:
        return True
    # Returns False if otherwise.
    return False