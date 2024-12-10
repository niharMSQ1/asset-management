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

import json
import requests

from .dbUtils import get_connection
from .ezOfficeInventoryUtils import *
from .helper import get_location_with_geopy
from .invGateApiUtils import *
from .ibmMaximoUtils import *
from .models import HardwareAssetsServiceNow
from .servicenowApiUtils import *
from .zohoApiUtil import zoho_main


# Create your views here.
@csrf_exempt
def get_hardware_details_and_save(request):
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
            
            for i in hardware_data:
                # Fetch and validate data from ServiceNow API
                inventory_number = i.get("asset_tag", "").strip()
                item_name = i.get("display_name", "").strip()
                category = ""
                try:
                    model_category_link = i.get("model_category", {}).get("link")
                    if model_category_link:
                        category_response = requests.get(model_category_link, headers=headers, auth=auth)
                        category = category_response.json().get("result", {}).get("name", "").strip()
                except Exception:
                    category = ""

                location = ""
                try:
                    location_link = i.get("location", {}).get("link")
                    if location_link:
                        location_response = requests.get(location_link, headers=headers, auth=auth)
                        location_data = location_response.json().get("result", {})
                        latitude = location_data.get("latitude")
                        longitude = location_data.get("longitude")
                        if latitude and longitude:
                            location = get_location_with_geopy(latitude, longitude)
                except Exception:
                    location = ""

                warranty_info = i.get("warranty_expiration", "").strip()
                serial_number = i.get("serial_number", "").strip()
                bank_loan = False  # Not available in ServiceNow response
                purchase_date = parse_date(i.get("purchase_date", ""))
                current_value = float(i.get("cost", 0.0) or 0.0)
                salvage_value = float(i.get("salvage_value", 0.0) or 0.0)
                notes = i.get("work_notes", "").strip()
                depreciation_annual = 0.0
                depreciation_monthly = 0.0
                expected_life_years = 1
                asset_end_date = None

                try:
                    depreciation_link = i.get("depreciation", {}).get("link")
                    if depreciation_link:
                        depreciation_response = requests.get(depreciation_link, headers=headers, auth=auth)
                        depreciation_data = depreciation_response.json().get("result", {})
                        expected_life_years = int(depreciation_data.get("depreciation_time", 1))
                        if expected_life_years > 0:
                            depreciation_annual = (current_value - salvage_value) / expected_life_years
                            depreciation_monthly = depreciation_annual / 12
                        if purchase_date:
                            asset_end_date = purchase_date + timedelta(days=expected_life_years * 365)
                except Exception:
                    pass

                months_to_replace = 36  # Example default, customize as per requirement
                three_month_end_alert = (asset_end_date and asset_end_date - timedelta(days=90) <= date.today()) if asset_end_date else False


                # Prepare data for logging
                saved_data = {
                    "inventory_number": inventory_number,
                    "item_name": item_name,
                    "category": category,
                    "location": location,
                    "warranty_info": warranty_info,
                    "serial_number": serial_number,
                    "bank_loan": bank_loan,
                    "purchase_date": purchase_date,
                    "expected_life_years": expected_life_years,
                    "asset_end_date": asset_end_date,
                    "months_to_replace": months_to_replace,
                    "three_month_end_alert": three_month_end_alert,
                    "purchase_price": current_value,
                    "end_of_life_expected_value": salvage_value,
                    "straight_line_depreciation_annual": depreciation_annual,
                    "straight_line_depreciation_monthly": depreciation_monthly,
                    "current_value": current_value,
                    "notes": notes,
                }

                # Log the data
                print("Data being saved:", saved_data)
                print("-" * 80)

                # Save data to the model
                HardwareAssetsServiceNow.objects.update_or_create(
                    inventory_number=inventory_number,
                    serial_number=serial_number,
                    defaults=saved_data,
                )

        return JsonResponse({"status": "success"}, status=200)

    except requests.RequestException as e:
        return JsonResponse({"error": f"Failed to fetch data: {str(e)}"}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
def get_hardware_details(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    try:
        body = json.loads(request.body)
        token = body[0].get("token")
        if token != settings.TOKEN_FROM_PHP:
            return JsonResponse({"error": "Token not valid"}, status=401)

        organization_id = body[0].get("organization_id")
        tool = body[0].get("tool")

        if not organization_id or not tool:
            return JsonResponse({"error": "Missing required parameters: 'organization_id' and 'tool'."}, status=400)

        if tool == "ServiceNow":
            response, status = fetch_and_store_servicenow_data(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "InvGate":
            response, status = fetch_and_store_invGate_data(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "IBM-Maximo":
            response, status = fetch_and_store_ibm_maximo_data(organization_id, tool, body="")
            return JsonResponse(response, status=status)
        elif tool == "ezofficeinventory":
            response, status = fetch_and_store_ibm_ezofficeinventory_data(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "zoho":
            response, status = zoho_main(organization_id, tool, body)
            return JsonResponse(response, status=status)

        return JsonResponse({"error": f"Unsupported tool: {tool}"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

@csrf_exempt
def get_objects_by_org_id(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        body = json.loads(request.body)
        token = body[0].get("token")
        if token != settings.TOKEN_FROM_PHP:
            raise Exception("Token not valid")
        org_id = body[0].get("organization_id")
        tool = body[0].get("tool")

        if not org_id or not tool:
            return JsonResponse({"error": "Missing required parameters"}, status=400)
        
        if tool =="Servicenow":

            connection = get_connection()
            if not connection:
                return JsonResponse({"error": "Failed to connect to the database"}, status=500)

            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT * 
                    FROM compliance_integrations 
                    WHERE organization_id = %s AND tool = %s
                """
                cursor.execute(query, (org_id, tool))
                result = cursor.fetchall()

            if not result:
                return JsonResponse({"error": "No matching data found"}, status=404)

            api_credentials = json.loads(result[0].get("api_credentials"))
            url = f"{api_credentials['api_url']}/api/now/table/{settings.SERVICENOW_TABLE}"
            username = api_credentials["api_key"]
            password = api_credentials["api_end_ponit"]
            auth = (username, password)

            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGO_DB_NAME]
            collection = db[settings.MONGO_COLLECTION_NAME]
            objects = collection.find({"org_id": org_id}, {"_id": 0})
            objects_list = list(objects)

            return JsonResponse({"status": "success", "data": objects_list}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
    
