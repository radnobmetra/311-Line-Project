import requests


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
