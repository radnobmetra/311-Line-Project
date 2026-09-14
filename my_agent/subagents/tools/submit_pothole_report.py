import json

def submit_report(location:str) -> str:
    """
    Placeholder function in lieu of reporting to a tracking system

    Args:
        location (str): location of where the pothole occurs
    
    Returns:
        status (str):
            "Successly Reported" if a location is given, else returns an error.

    
    
    """
    status = "";
    if location == "":
        status = "An Error has occured, no valid address"
    else:
        status = "Successly Reported"
        print(location)

    return status

