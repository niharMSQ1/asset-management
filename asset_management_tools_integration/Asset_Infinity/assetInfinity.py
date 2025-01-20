import requests
import json
from django.conf import settings
from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime
from ..dbUtils import get_connection


def fetch_and_store_asset_infinity_data(organization_id, tool, body):
    connection = get_connection()
    if not connection:
        return {"error": "Failed to connect to the database."}, 500
    
    compliance_id = body[0].get("id")
    
    with connection.cursor(dictionary=True) as cursor:
        query = """
                    SELECT * 
                    FROM compliance_integrations 
                    WHERE id = %s
                """
        cursor.execute(query, (compliance_id,))
        
        result = cursor.fetchall()
        API_BASE_URL = "https://api.assetinfinity.io/api/asset-list"
        API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjEyODUiLCJjb21wYW55Ijoic2VjcXVyZW9uZSIsImVtYWlsIjoibmloYXIubUBzZWNxdXJlb25lLmNvbSIsImRhdGVGb3JtYXQiOiJkZC9NTS95eXl5IGhoOm1tIHR0IiwidGltZVpvbmUiOiJJbmRpYSBTdGFuZGFyZCBUaW1lIiwiZGV2aWNlSWQiOiI3MTQ2MUIyMC0zNkY2LTQyQ0ItQUQ1My0yMUFBNDE1NDUzNEQiLCJ1c2VyVHlwZUlkIjoiMiIsIm5iZiI6MTczNDQyMTk1NiwiZXhwIjoxODkyMTAyMjU2LCJpYXQiOjE3MzQ0MjE5NTZ9.HzDPBqPn63jlIeR9I3c-bK0K7xyjm1YBpM-0vdOELig"

        HEADERS = {
            "Authorization": f"Bearer: {API_KEY}",
            "Content-Type":	"application/json"
        }

        params = {"page": 1, "pageSize": 100}

        response = requests.get(API_BASE_URL, headers=HEADERS, params=params)

        if response.status_code == 200:
            assets = response.json()
            
            # MongoDB Integration
            try:
                client = MongoClient(settings.MONGO_URI)
                db = client[settings.MONGO_DB_NAME]
                collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS]

                # Store the data in MongoDB
                collection.insert_many(assets.get("assets", []))
                print(f"{len(assets.get('assets', []))} assets stored successfully.")
            except Exception as e:
                print(f"Failed to store assets in MongoDB: {e}")
            finally:
                client.close()
            
            return assets
        else:
            print(f"Failed to fetch assets. Status code: {response.status_code}")
            print(f"Error: {response.text}")
            return None