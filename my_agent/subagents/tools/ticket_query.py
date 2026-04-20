import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import re


def validate_ticket_num_format(ticket_number):
    """
    Ticket number must exactly match this format (6 digits, a dash, then 7 digits).
    For example, ticket number should be like this "123456-1234567"
    If a dash is missing, it will be added.

    Returns:
    True and the ticket number
    or
    False and empty string if ticket number isn't valid
    """
    validated_number = ticket_number

    # First check: checks if exact match.
    pattern = r"\d{6}-\d{7}"
    match = re.fullmatch(pattern, ticket_number)

    # Second check: checks if a dash is missing.
    if match is None:
        pattern = r"\d{13}"
        match = re.fullmatch(pattern, ticket_number)

        # Add a dash if it's missing.
        if match is not None:
            validated_number = ticket_number[:6] + "-" + ticket_number[6:]
        else:
            validated_number = ""

    is_correct_format = match != None

    return is_correct_format, validated_number


def convert_Epoch_to_localtime(epoch_time):
    """
    Time retrieved from the ArcGIS database is stored as UNIX Epoch time.
    This function converts epoch time to local time.
    For example, 1776148140000 will be converted to 04/13/2026 11:29 PM
    """
    formatted_time = ""

    # If the inputted time is null/empty, the function will return empty string.
    if epoch_time != None:
        # Epoch time is in milliseconds. Divide it by 1000 to convert it to seconds.
        epoch_time = epoch_time / 1000.0

        datetime_obj = datetime.fromtimestamp(
            epoch_time, tz=ZoneInfo("America/Los_Angeles")
        )
        formatted_time = datetime_obj.strftime("%m/%d/%Y %I:%M %p")

    return formatted_time


def ArcGIS_get_ticket(ticket_number):
    """
    A GET function to fetch ticket data from ArcGIS API endpoint.

    Returns a JSON with 2 fields: status and message containing ticket information.
    """
    response_JSON = {"status": "", "message": ""}

    try:
        endpoint = "https://services5.arcgis.com/54falWtcpty3V47Z/arcgis/rest/services/SalesForce311_View/FeatureServer/0/query"
        payload = {
            "where": f"(ReferenceNumber='{ticket_number}')",
            "outFields": "*",
            "f": "pjson",
        }

        req_response = requests.get(endpoint, params=payload)
        req_response.raise_for_status()  # Raises an exception if HTTP error occured.

        response_JSON["status"] = "success"
        response_JSON["message"] = req_response.json()["features"][0]["attributes"]
    except Exception as e:
        # This will catch any type of error. Return error details in JSON format.
        response_JSON["status"] = "error"
        response_JSON["message"] = f"ArcGIS API request failed: {e}"

    return response_JSON
