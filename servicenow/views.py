from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from .helper import convertJsonToExcel

# Create your views here.
def home(request):
    return JsonResponse({
        "message":"Hello World"
    })

@csrf_exempt
def get_hardware_details(request):
    url = f"{settings.SERVICENOW_INSTANCE}/api/now/table/{settings.SERVICENOW_TABLE}"
    headers = {
        "Accept": "application/json",
    }
    auth = (settings.SERVICENOW_USER, settings.SERVICENOW_PASSWORD)

    try:
        response = requests.get(url, headers=headers, auth=auth)
        if response.status_code == 200:
            data = response.json()
            convertJsonToExcel(data)
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse(
                {"error": f"Failed to fetch data, status code: {response.status_code}"},
                status=response.status_code,
            )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)