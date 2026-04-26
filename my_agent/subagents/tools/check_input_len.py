from timertracker import update_user_status

def check_input_len(user_input: str) -> bool:
    """
    Counts the number of chars in the user's input and ensures that 70% of the input is made up of alphanumeric characters.

    Args:
        user_input (str): The user input to check.

    Returns:
        bool: True if 70% or more of the characters in the user's input are alphanumeric chars, False otherwise.
    """
    # logs activity first when ran
    update_user_status("user", user_input) 
    
    # character check logic
    counter = 0
    # Progresses through each character in the user input.
    for char in user_input:
        if (char.isalnum()):
            counter = counter + 1
    # Returns True if the user's input is at least 70% alphanumeric characters.
    if counter / len(user_input) >= 0.7:
        return True
        
    # Returns False if otherwise.
    return False