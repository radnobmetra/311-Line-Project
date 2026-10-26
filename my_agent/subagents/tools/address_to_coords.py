from google.adk.tools.tool_context import ToolContext
from geopy.geocoders import ArcGIS

def get_coordinates(address: str, tool_context: ToolContext) -> tuple:
    geolocator = ArcGIS()
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        
        tool_context.state["outcome_label"] = "Address geocoding failed: location not found."
        return None
    except Exception as e:
        tool_context.state["outcome_label"] = f"ArcGIS Geocoding error: {e}"
        print(f"Geocoding error: {e}")
        return None