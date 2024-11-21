import requests
import json

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .helper import convertJsonToExcel, get_location_with_geopy

# Create your views here.
def test(request):
    return JsonResponse({
        "message":"Hello World!"
    })

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
            
            for i in (data.get("result")):
                inventory_number = (i.get("asset_tag")) # in db
                condition = "" # in db but not in servicenow response
                item_name =(i.get("display_name")) # in db
                category = ((((requests.get(((i.get("model_category"))).get("link") , headers = headers, auth = auth))).json()).get("result")).get("name") # in db
                area = requests.get(((i.get("location"))).get("link") , headers = headers, auth = auth) # Not required to save in db
                location = get_location_with_geopy(json.loads(area.text)['result']['latitude'], json.loads(area.text)['result']['longitude']) # in db
                warranty_info = (i.get("warranty_expiration")) # in db
                serial_number = (i.get("serial_number")) # in db
                bank_loan = "" # in db but not in servicenow response
                current_value = (i.get("cost")) # in db
                salvage_value = i.get("salvage_value") # in response, not required in db
                purchase_date = (i.get("purchase_date")) # in db
                depreciation = requests.get(((i.get("depreciation"))).get("link") , headers = headers, auth = auth) # value required to save in db
                depreciation_data = json.loads(depreciation.text) # value required to save in db
                useful_life = int(depreciation_data["result"]["depreciation_time"]) # in response, not required in db
                straight_line_depreciation_annual = (current_value - salvage_value) / useful_life # in db
                straight_line_depreciation_monthly = straight_line_depreciation_annual / 12 # in db
                end_of_life_expected_value = "" # in db but not in servicenow response
                notes = (i.get("work_notes"))  # in db

                '''
                items not in servicenow response

                1. condition
                2. bank_loan
                3. end_of_life_expected_value

                '''

            convertJsonToExcel(data)
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse(
                {"error": f"Failed to fetch data, status code: {response.status_code}"},
                status=response.status_code,
            )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
