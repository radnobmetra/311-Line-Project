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
        # checking if each character is ascii.
        if char.isascii():
            counter += 1
    # Returns True if the user's input is at least 70% ASCII characters.
    if counter / len(user_input) >= 0.7:
        return True
    # Returns False if otherwise.
    return False