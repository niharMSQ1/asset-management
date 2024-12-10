import requests
from django.http import JsonResponse

def fetch_and_store_ibm_ezofficeinventory_data(organization_id, tool, body):
    API_KEY = (body[0]).get("company_token")
    SUBDOMAIN = (body[0]).get("subdomain")
    url = f"{SUBDOMAIN}/assets.api"
    
    params = {
        "include_custom_fields": "true",
        "show_document_urls": "true",
        "show_image_urls": "true",
        "show_document_details": "true",
        "page": 1  # Start with the first page
    }
    
    headers = {
        "Authorization": f"token: {API_KEY}"
    }

    all_assets = []
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                assets = data.get("assets", [])
                all_assets.extend(assets)
                if not data.get("next_page", None):
                    break
                params["page"] += 1
            else:
                return {
                    "error": "Failed to fetch assets",
                    "status": response.status_code,
                    "message": response.text
                }, response.status_code
    except Exception as e:
        return {
            "error": "An error occurred while fetching assets",
            "details": str(e)
        }, 500
    
    return {
        "total_assets": len(all_assets),
        "assets": all_assets
    }, 200
