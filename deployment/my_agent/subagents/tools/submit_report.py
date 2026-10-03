import json
import random

def submit_report(report_type: str, location: str, details: str = "None provided", photo_url: str = "None provided") -> str:
    """
    Placeholder function in lieu of reporting to a tracking system.

    Args:
        report_type (str): Type of report (e.g., 'pothole', 'streetlight', 'parking_meter').
        location (str): location of where the issue occurs.
        details (str): Additional specifics like pole numbers, meter IDs, or descriptions.
        photo_url (str): URL of the submitted photo.
    
    Returns:
        status (str): A JSON string containing the success status and ticket number, or an error.
    """
    if location == "":
        return json.dumps({"status": "Error", "message": "An Error has occured, no valid address"})
    
    prefixes = {
        "pothole": "PH",
        "streetlight": "SL",
        "parking_meter": "PM"
    }
    
    # set prefix if any
    prefix = prefixes.get(report_type.lower(), "GN") 
    ticket_id = f"{prefix}-{random.randint(1000, 9999)}"
    
    print(f"Logged [{ticket_id}] {report_type.upper()} at {location} | Details: {details} | Photo: {photo_url}")

    return json.dumps({
        "status": "Successfully Reported",
        "ticket_number": ticket_id,
        "report_type": report_type
    })