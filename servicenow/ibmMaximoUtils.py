import requests
import json
from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from .dbUtils import get_connection
from django.conf import settings

def fetch_and_store_ibm_maximo_data(organization_id, tool, body):
    username = settings.IBM_MAXIMO_USERNAME
    password = settings.IBM_MAXIMO_PASSWORD
    base_url = settings.IBM_MAXIMO_URL + "/maximo/oslc/os/mxasset"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    assets = []
    start_index = 1
    page_size = 100
    
    while True:
        params = {
            "oslc.select": "*",  # Fetch all attributes
            "oslc.pageSize": page_size,
            "oslc.startIndex": start_index,
            "username": username,  # Add username to params
            "password": password   # Add password to params
        }

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if "rdfs:member" in data:
                assets.extend(data["rdfs:member"])
                print(f"Fetched {len(data['rdfs:member'])} assets.")
                start_index += page_size
            else:
                print("No more assets to fetch.")
                break
        else:
            print(f"Error fetching assets: {response.status_code} - {response.text}")
            break

    return assets
