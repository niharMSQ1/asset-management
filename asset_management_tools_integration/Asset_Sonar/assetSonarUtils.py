import requests
import json
from django.conf import settings
from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime
from ..dbUtils import get_connection


def fetch_and_store_asset_sonar_data(organization_id, tool, body):
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
        API_BASE_URL = settings.ASSET_SONAR_API_URL + "assets.api"
        API_KEY = settings.ASSET_SONAR_API_KEY

        HEADERS = {
            "Authorization": f"token: {API_KEY}"
        }

        params = {
            "include_custom_fields": "true",
            "show_document_urls": "true",
            "show_image_urls": "true",
            "show_document_details": "true",
            "page": 1
        }

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