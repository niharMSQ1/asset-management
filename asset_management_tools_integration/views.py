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
from .helper import get_location_with_geopy


from .EZ_Office_Inventory.ezOfficeInventoryUtils import *
from .InvGate.invGateApiUtils import *
from .Servicenow.servicenowApiUtils import *
from .Zoho.zohoApiUtil import *
from .InvGate.invGateApiUtils import *
from .Asset_Infinity.assetInfinity import *
from .EZ_Office_Inventory.ezOfficeInventoryUtils import *
from .Asset_Sonar.assetSonarUtils import *
from .Upkeep.upKeepUtils import *


# from .models import HardwareAssetsServiceNow

# Create your views here.
@csrf_exempt
def get_hardware_details(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    try:
        body = json.loads(request.body)
        token = body[0].get("token")
        if token != settings.ACCESS_TOKEN_PY:
            return JsonResponse({"error": "Token not valid"}, status=401)

        organization_id = body[0].get("organization_id") if body[0].get("organization_id") else "NA"
        tool = body[0].get("tool")

        if not organization_id or not tool:
            return JsonResponse({"error": "Missing required parameters: 'organization_id' and 'tool'."}, status=400)

        if tool == "servicenow":
            response, status = fetch_and_store_servicenow_data(organization_id, tool, body)
            if status == 200:
                return JsonResponse(
                    {
                        "message": response,
                        "Status": response.get("status")
                    },
                    status=status
                )
                
            # elif status == 401:
            #     return JsonResponse(
            #         {
            #             "message": response.get("error"),
            #             "Status": "Failed"
            #         },
            #         status=status pause1
            #     )
            elif status ==  401 or status ==  500:
                return JsonResponse(
                    {
                        "message": "Please enter correct details",
                        "status": "Failed"
                    },
                    status=status
                )
        elif tool == "InvGate":
            response, status = fetch_and_store_invGate_data(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "ezofficeinventory":
            response, status = fetch_and_store_ezofficeinventory_data(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "zoho":
            
            response, status = zoho_main(organization_id, tool, body)
            return JsonResponse(response, status=status)
        elif tool == "zohoHRM":
            
            response, status = zoho_main(organization_id, tool, body)
            return JsonResponse(response, status=status)
        
        elif tool == "UpKeep":
            response, status = upkeep_main(organization_id, tool, body)
            return JsonResponse(response, status=status)
        
        # elif tool == "odooAssets":
        #     response, status = odooAssetInventry(organization_id, tool, body)
        #     return JsonResponse(response, status=status)
        
        # elif tool == "odooEmployees":
        #     response, status = odooEmployeeDetails(organization_id, tool, body)
        #     return JsonResponse(response, status=status)

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
        
        if tool =="servicenow":

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
            collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS]
            objects = collection.find({"org_id": org_id}, {"_id": 0})
            objects_list = list(objects)

            return JsonResponse({"status": "success", "data": objects_list}, status=200)
        
        # elif tool == "zoho":
            

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
    
@csrf_exempt
def validate_tool_credentials(request):
    body = json.loads(request.body)
    
    if (body[0]).get("tool") == "zohoHRM":
        client_id = ((body[0]).get("credentials")).get("CLIENT_ID")
        client_secret = ((body[0]).get("credentials")).get("CLIENT_SECRET")
        domain  = ((body[0]).get("credentials")).get("domain")
        
        data = [{
            "AUTH_CODE":(body[0]['credentials']).get("AUTH_CODE"),
            "CLIENT_ID":client_id,
            "CLIENT_SECRET":client_secret
        }]
        
        req = generate_access_refresh_token_zoho(data)
        
        if "access_token" in req:
        
            return JsonResponse({
                "Status":"Success",
                "data": {
                    "client_id":client_id,
                    "client_secret":client_secret,
                    "url":domain,
                    "refresh_token":req.get('refresh_token'),
                    "access_token":req.get('access_token')
                }
                
            },status = 200)
        else:
            return JsonResponse({
                "Status":"Failed",
                
            },status = 500)