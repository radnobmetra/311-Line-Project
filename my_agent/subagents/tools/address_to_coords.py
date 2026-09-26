from geopy.geocoders import ArcGIS

def get_coordinates(address: str) -> tuple:
    """
    this takes a street address and returns a (latitude, longitude) tuple.
    """
    geolocator = ArcGIS()
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None