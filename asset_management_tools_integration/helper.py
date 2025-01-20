import pandas as pd
from pandas import json_normalize
from geopy.geocoders import Nominatim

def convertJsonToExcel(json_data):
    df = json_normalize(json_data, sep='_')
    output_file = "nested_output.xlsx"
    df.to_excel(output_file, index=False)
    return

def get_location_with_geopy(lat, long):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, long), language="en")
    if location:
        return location.address
    else:
        return "Location not found"
