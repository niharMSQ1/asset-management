import requests
import socket, json
from pymongo import MongoClient
from django.http import JsonResponse
from django.conf import settings
from dateutil.parser import parse as parse_date
from .dbUtils import get_connection 


def fetch_and_store_servicenow_data(organization_id, tool, body):
    # connection = get_connection()
    # if not connection:
    #     return {"error": "Failed to connect to the database."}, 500

    try:
        # with connection.cursor(dictionary=True) as cursor:
        #     query = """
        #         SELECT * 
        #         FROM compliance_integrations 
        #         WHERE organization_id = %s AND tool = %s
        #     """
        #     cursor.execute(query, (organization_id, tool))
        #     result = cursor.fetchall()

        # if not result:
        #     return {"error": "No matching compliance integrations found."}, 404

        url = ((body[0]).get("credentials").get("url")) +"/api/now/table/"+settings.SERVICENOW_TABLE
        username =  ((body[0]).get("credentials").get("api_end_ponit"))
        password = ((body[0]).get("credentials").get("api_key"))

        if not url or not username or not password:
            return {"error": "Invalid or missing API credentials."}, 500

        headers = {"Accept": "application/json"}
        auth = (username, password)

        response = requests.get(url, headers=headers, auth=auth)
        response.raise_for_status()

        data = response.json()
        hardware_data = data.get("result", [])

        filtered_hardware_data = []
        for item in hardware_data:
            inventory_number = item.get("asset_tag", "").strip()
            item_name = item.get("display_name", "").strip()
            warranty_info = item.get("warranty_expiration", "").strip()
            serial_number = item.get("serial_number", "").strip()
            purchase_date = parse_date(item.get("purchase_date", "")) if item.get("purchase_date") else None
            current_value = float(item.get("cost", 0.0) or 0.0)
            salvage_value = float(item.get("salvage_value", 0.0) or 0.0)
            notes = item.get("work_notes", "").strip()

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
            "data": hardware_data
        }, 200
    except requests.RequestException as e:
        return {"error": str(e)}, 401 
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}, response.status_code
    
