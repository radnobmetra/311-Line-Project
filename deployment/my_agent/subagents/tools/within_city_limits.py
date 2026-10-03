import os
import geopandas as geopanda
from shapely.geometry import Point
from .address_to_coords import get_coordinates

def verify_address(address: str) -> dict:
    """
    calls get_coordinates to retrieve location data, then verifies 
    if it falls within sac  limits.
    """
    # address2coords tool
    coords = get_coordinates(address)
    
    if not coords:
        return {
            "verified": False,
            "lat": None,
            "lng": None,
            "message": "Error address not found."}
        
    lat, lng = coords
    
    # boundary logic
    coords_point = Point(lng, lat) # Shapely uses (longitude, latitude)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "SacramentoCityLimits.geojson")
    
    city_limits = geopanda.read_file(file_path)
    within_limits = city_limits.contains(coords_point)
    is_verified = bool(within_limits[0])
    
    # return compiled data
    return {
        "verified": is_verified,
        "lat": lat,
        "lng": lng,
        "message": "Within limits." if is_verified else "Outside limits."
    }