import json

def submit_report(location:str) -> str:

    """
    placeholder for tracking system 

    Args:
        location (str): location of where parking meter is found broken

    Returns:
        status (str):
        
    """

    status = "";
    if location == "":
        status = "An Error has occured, no valid address"
    else:
        status = "Successly Reported"
        print(location)
    
    return status