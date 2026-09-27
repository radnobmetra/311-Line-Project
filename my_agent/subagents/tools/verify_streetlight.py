import requests
import json

def verify_streetlight(pole_number: str) -> str:
    """
    queries sac ArcGIS database to verify if a specfied streetlight exists.
   
    """
    # api endpoint and params
    url = "https://services5.arcgis.com/54falWtcpty3V47Z/arcgis/rest/services/Street_Lights/FeatureServer/0/query"
    
    params = {
        "where": f"ASSET_ID='{pole_number}' OR OBJ_CODE='{pole_number}'",
        "outFields": "*",
        "outSR": "4326",
        "f": "json"
    }
    
    try:
        # ping the server
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # verify pole exists
        if "features" in data and len(data["features"]) > 0:
            
            # return compiled data
            pole_data = data["features"][0]["attributes"]
            return json.dumps({
                "verified": True,
                "message": "Streetlight verified in city database!",
                "details": {
                    "asset_id": pole_data.get("ASSET_ID"),
                    "type": pole_data.get("POLE_TYPE"),
                    "wattage": pole_data.get("WATTAGE")
                }
            })
        
        # return not found
        return json.dumps({
            "verified": False,
            "message": f"No streetlight found matching number {pole_number}.."
        })
            
    except requests.exceptions.RequestException as e:
        
        # error handling
        return json.dumps({
            "verified": False,
            "message": f"API connection error: {str(e)}"
        })