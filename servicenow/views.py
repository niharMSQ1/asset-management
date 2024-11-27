from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta, date
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient

import requests

from .helper import get_location_with_geopy
from .models import HardwareAssetsServiceNow


# Create your views here.
# @csrf_exempt
# def get_hardware_details(request):
#     url = f"{settings.SERVICENOW_URL}/api/now/table/{settings.SERVICENOW_TABLE}"
#     headers = {
#         "Accept": "application/json",
#     }
#     auth = (settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD)

#     try:
#         response = requests.get(url, headers=headers, auth=auth)
#         if response.status_code == 200:
#             data = response.json()
#             hardware_data = data.get("result", [])
            
#             for i in hardware_data:
#                 # Fetch and validate data from ServiceNow API
#                 inventory_number = i.get("asset_tag", "").strip()
#                 item_name = i.get("display_name", "").strip()
#                 category = ""
#                 try:
#                     model_category_link = i.get("model_category", {}).get("link")
#                     if model_category_link:
#                         category_response = requests.get(model_category_link, headers=headers, auth=auth)
#                         category = category_response.json().get("result", {}).get("name", "").strip()
#                 except Exception:
#                     category = ""

#                 location = ""
#                 try:
#                     location_link = i.get("location", {}).get("link")
#                     if location_link:
#                         location_response = requests.get(location_link, headers=headers, auth=auth)
#                         location_data = location_response.json().get("result", {})
#                         latitude = location_data.get("latitude")
#                         longitude = location_data.get("longitude")
#                         if latitude and longitude:
#                             location = get_location_with_geopy(latitude, longitude)
#                 except Exception:
#                     location = ""

#                 warranty_info = i.get("warranty_expiration", "").strip()
#                 serial_number = i.get("serial_number", "").strip()
#                 bank_loan = False  # Not available in ServiceNow response
#                 purchase_date = parse_date(i.get("purchase_date", ""))
#                 current_value = float(i.get("cost", 0.0) or 0.0)
#                 salvage_value = float(i.get("salvage_value", 0.0) or 0.0)
#                 notes = i.get("work_notes", "").strip()
#                 depreciation_annual = 0.0
#                 depreciation_monthly = 0.0
#                 expected_life_years = 1
#                 asset_end_date = None

#                 try:
#                     depreciation_link = i.get("depreciation", {}).get("link")
#                     if depreciation_link:
#                         depreciation_response = requests.get(depreciation_link, headers=headers, auth=auth)
#                         depreciation_data = depreciation_response.json().get("result", {})
#                         expected_life_years = int(depreciation_data.get("depreciation_time", 1))
#                         if expected_life_years > 0:
#                             depreciation_annual = (current_value - salvage_value) / expected_life_years
#                             depreciation_monthly = depreciation_annual / 12
#                         if purchase_date:
#                             asset_end_date = purchase_date + timedelta(days=expected_life_years * 365)
#                 except Exception:
#                     pass

#                 months_to_replace = 36  # Example default, customize as per requirement
#                 three_month_end_alert = (asset_end_date and asset_end_date - timedelta(days=90) <= date.today()) if asset_end_date else False


#                 # Prepare data for logging
#                 saved_data = {
#                     "inventory_number": inventory_number,
#                     "item_name": item_name,
#                     "category": category,
#                     "location": location,
#                     "warranty_info": warranty_info,
#                     "serial_number": serial_number,
#                     "bank_loan": bank_loan,
#                     "purchase_date": purchase_date,
#                     "expected_life_years": expected_life_years,
#                     "asset_end_date": asset_end_date,
#                     "months_to_replace": months_to_replace,
#                     "three_month_end_alert": three_month_end_alert,
#                     "purchase_price": current_value,
#                     "end_of_life_expected_value": salvage_value,
#                     "straight_line_depreciation_annual": depreciation_annual,
#                     "straight_line_depreciation_monthly": depreciation_monthly,
#                     "current_value": current_value,
#                     "notes": notes,
#                 }

#                 # Log the data
#                 print("Data being saved:", saved_data)
#                 print("-" * 80)

#                 # Save data to the model
#                 HardwareAssetsServiceNow.objects.update_or_create(
#                     inventory_number=inventory_number,
#                     serial_number=serial_number,
#                     defaults=saved_data,
#                 )

#         return JsonResponse({"status": "success"}, status=200)

#     except requests.RequestException as e:
#         return JsonResponse({"error": f"Failed to fetch data: {str(e)}"}, status=500)

#     except Exception as e:
#         return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
def get_hardware_details(request):
    url = f"{settings.SERVICENOW_URL}/api/now/table/{settings.SERVICENOW_TABLE}"
    headers = {
        "Accept": "application/json",
    }
    auth = (settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD)

    try:
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            data = response.json()
            hardware_data = data.get("result", [])

            filtered_hardware_data = []
            for i in hardware_data:
                inventory_number = i.get("asset_tag", "").strip()
                item_name = i.get("display_name", "").strip()
                warranty_info = i.get("warranty_expiration", "").strip()
                serial_number = i.get("serial_number", "").strip()
                purchase_date = parse_date(i.get("purchase_date", "")) if i.get("purchase_date") else None
                current_value = float(i.get("cost", 0.0) or 0.0)
                salvage_value = float(i.get("salvage_value", 0.0) or 0.0)
                notes = i.get("work_notes", "").strip()

                if purchase_date:
                    purchase_date = purchase_date.strftime('%Y-%m-%d')

                filtered_hardware_data.append({
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

            for item in filtered_hardware_data:
                serial_number = item["serial_number"]
                if serial_number:
                    collection.update_one(
                        {"serial_number": serial_number},
                        {"$set": item},
                        upsert=True
                    )

            return JsonResponse({"status": "success", "total_objects": len(filtered_hardware_data)}, status=200)

        return JsonResponse({"error": "Failed to fetch data from ServiceNow"}, status=response.status_code)

    except requests.RequestException as e:
        return JsonResponse({"error": f"Failed to fetch data: {str(e)}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)