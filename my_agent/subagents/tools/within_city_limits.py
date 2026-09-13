import pandas as panda
import geopandas as geopanda
from shapely.geometry import Point



def within_city_limits(
    coordinates_raw:str
) -> bool:
    """
    Checks to see if a given set of coordinates are within city limits.
    Has a preset file (SacramentoCityLimits).geojson which data is dervied from.

    Args: 
        user_input (str): The user input, comes as a space seperated coordinate string.

    Returns:
        bool: True if the coordinates are in city limits. False if outside of city limits.    
    """
    coords = coordinates_raw.split(" ")
    latitude_value = float(coords[0])
    longitude_value = float(coords[1])
    coords2 = Point(longitude_value, latitude_value)
    file = open("311-Line-Project\\my_agent\\subagents\\tools\\SacramentoCityLimits.geojson")
    city_limits = geopanda.read_file(file)
    city_limits_mask = (city_limits.loc[0,'geometry'])
    

    within_limits = city_limits.contains(coords2)

    print(within_limits[0])
    return city_limits


