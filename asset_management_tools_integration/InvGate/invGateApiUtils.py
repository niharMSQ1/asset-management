import json
import requests

from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from .. import dbUtils
from django.conf import settings

def fetch_and_store_invGate_data(organization_id, tool, body):
    token_url = f"{body[0]["INVGATE_URL"]}/oauth2/token/"
    assets_url = f"{body[0]["INVGATE_URL"]}/public-api/v2/assets-lite/"
    
    try:
        token_response = requests.post(
            token_url,
            params={
                "grant_type": "client_credentials",
                "client_id": body[0]["INVGATE_CLIENT_ID"],
                "client_secret": body[0]["INVGATE_CLIENT_SECRET"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}  # Adjust content type if required
        )

        if token_response.status_code != 200:
            return {"error": "Failed to get access token", "details": token_response.json()}



        
        access_token = token_response.json().get("access_token")

        assets_response = requests.get(
            assets_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        if assets_response.status_code == 200:
            all_assets =(assets_response.json()).get("results")
            filtered_hardware_data = []
            for item in all_assets:
                inventory_number = item.get("inventory_id", "").strip()
                item_name = item.get("name", "").strip()
                warranty_info = None
                serial_number = item.get("serial", "")
                purchase_date = parse_date(item.get("created_at", "")) if item.get("created_at") else None
                current_value = float(item.get("finance", 0.0) or 0.0)
                salvage_value = None
                notes = None

                if purchase_date:
                    purchase_date = purchase_date.strftime('%Y-%m-%d')

                filtered_hardware_data.append({
                    "org_id": organization_id,
                    "inventory_number": inventory_number,
                    "item_name": item_name,
                    "warranty_info": warranty_info,
                    "serial_number": serial_number,
                    "purchase_date": purchase_date,
                    "current_value": current_value,
                    "salvage_value": salvage_value,
                    "notes": notes,
                })
            
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGO_DB_NAME]
            collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS]
            
            new_count = 0
            updated_count = 0

            for item in filtered_hardware_data:
                serial_number = item["serial_number"]
                if serial_number:
                    existing = collection.find_one({"serial_number": serial_number})
                    if existing:
                        if existing != item:
                            collection.update_one(
                                {"serial_number": serial_number},
                                {"$set": item},
                                upsert=False
                            )
                            updated_count += 1
                    else:
                        collection.insert_one(item)
                        new_count += 1

            return {
                "status": "success",
                "new_data_count": new_count,
                "updated_data_count": updated_count,
                "total_objects": len(filtered_hardware_data)
            }, 200
            
            return assets_response.json()
        else:
            return {"error": "Failed to retrieve assets", "details": assets_response.json()}
    
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "details": str(e)}