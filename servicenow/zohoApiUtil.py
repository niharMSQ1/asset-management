import requests
import json
from django.conf import settings
from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime

def generate_access_refresh_token_zoho(data):
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        return {"error": "Invalid input data format. Expected a list containing a dictionary."}
    
    auth_code = (data[0]).get("AUTH_CODE")
    client_id = (data[0]).get("CLIENT_ID")
    client_secret = (data[0]).get("CLIENT_SECRET")

    if not auth_code or not client_id or not client_secret:
        return {"error": "Missing required parameters: 'AUTH_CODE', 'CLIENT_ID', 'CLIENT_SECRET'."}

    zoho_token_url = "https://accounts.zoho.in/oauth/v2/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
    }

    try:
        response = requests.post(zoho_token_url, data=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        response_data = response.json()
        return response_data
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def refresh_zoho_access_token(refresh_token, client_id, client_secret,org_id):
    if not refresh_token or not client_id or not client_secret:
        return {"error": "Missing required parameters: 'REFRESH_TOKEN', 'CLIENT_ID', 'CLIENT_SECRET'."}

    zoho_token_url = "https://accounts.zoho.in/oauth/v2/token"
    params = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }

    try:
        response = requests.post(zoho_token_url, data=params, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get("access_token")
        if not access_token:
            return {"error": "Failed to refresh token. 'access_token' not found in response."}
        fetch_and_save_zoho_asset_details(access_token, org_id)
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def zoho_main(org_id, tool, data):
    if not isinstance(data, list) or not data:
        return {"error": "Invalid input 'data'. Expected a non-empty list."}, 400

    refresh_token = getattr(settings, "ZOHO_REFRESH_TOKEN", None)
    try:
        if not refresh_token:
            generate_refresh_access = generate_access_refresh_token_zoho(data)
            if "error" in generate_refresh_access:
                return generate_refresh_access, 400
            access_token = generate_refresh_access.get("access_token")
            if not access_token:
                return {"error": "Failed to retrieve 'access_token'."}, 400
            fetch_and_save_zoho_asset_details(access_token, org_id)
        else:
            access_token = getattr(settings, "ZOHO_ACCESS_TOKEN", None)
            if not access_token:
                return {"error": "'ZOHO_ACCESS_TOKEN' is not set in settings."}, 400
            return fetch_and_save_zoho_asset_details(access_token, org_id)
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}, 500

def fetch_and_save_zoho_asset_details(access_token, org_id):
    if not access_token:
        raise ValueError("Token not provided")

    zoho_api_url = "https://creator.zoho.in/api/v2/vinaykumar.a_sq1/it-asset-tracker/report/allmachines"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(zoho_api_url, headers=headers, timeout=10)
        if response.status_code == 401:
            refresh_response = refresh_zoho_access_token(
                refresh_token=getattr(settings, "ZOHO_REFRESH_TOKEN", None),
                client_id=getattr(settings, "ZOHO_CLIENT_ID", None),
                client_secret=getattr(settings, "ZOHO_CLIENT_SECRET", None),
                org_id=org_id
            )
            return JsonResponse(refresh_response, status=401)
        elif response.status_code == 200:
            data = response.json()
            hardware_data = data.get("data", [])
            filtered_hardware_data = []
            for item in hardware_data:
                inventory_number = item.get("ID", "").strip()
                warranty_info = item.get("Active_Service_Date", "").strip()
                serial_number = item.get("ID", "").strip()
                purchase_date = parse_date(item.get("Active_Service_Date", "")) if item.get("Active_Service_Date") else None
                name = item.get("Name", "").strip()
                type = (item.get("Type")).get("display_value")
                os = item.get("Operating_System", "").strip()
                
                if warranty_info:
                    warranty_info = datetime.strptime(warranty_info, '%d-%b-%Y')
                
                filtered_hardware_data.append({
                    "org_id":org_id,
                    "inventory_number":inventory_number,
                    "warranty_info":warranty_info,
                    "serial_number":serial_number,
                    "purchase_date":purchase_date,
                    "name":name,
                    "type":type,
                    "operating_system":os
                })
                
                client = MongoClient(settings.MONGO_URI)
                db = client[settings.MONGO_DB_NAME]
                collection = db[settings.MONGO_COLLECTION_NAME]
                
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

        else:
            return JsonResponse({
                "status": "error",
                "message": f"Failed to fetch assets. Zoho Creator API responded with status code {response.status_code}",
                "details": response.json()
            }, status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({
            "status": "error",
            "message": "An error occurred while making the request.",
            "details": str(e)
        }, status=500)
