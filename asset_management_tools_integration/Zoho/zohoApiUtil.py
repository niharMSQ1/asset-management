import requests
import json
from django.conf import settings
from dateutil.parser import parse as parse_date
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime
from ..dbUtils import get_connection

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
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def refresh_zoho_access_token(refresh_token, client_id, client_secret,org_id,tool, domain,compliance_id):
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
            raise ValueError("Access token not found in the response data.")
        connection = get_connection()
        with connection.cursor(dictionary=True) as cursor:
            query = '''
                    UPDATE compliance_integrations
                    SET response = JSON_SET(response, '$.data.access_token', %s)
                    WHERE id = %s
                '''
            cursor.execute(query, (access_token, compliance_id))
            connection.commit()
        if tool == "zoho":
            fetch_and_save_zoho_asset_details(access_token, org_id,tool, domain, refresh_token, compliance_id)
        elif tool == "zohoHRM":
            fetch_and_save_zoho_employee_details(access_token, org_id,tool, domain, refresh_token, compliance_id)
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def zoho_main(org_id, tool, data):
    if not isinstance(data, list) or not data:
        return {"error": "Invalid input 'data'. Expected a non-empty list."}, 400
    
    connection = get_connection()
    if not connection:
        return {"error": "Failed to connect to the database."}, 500
    
    compliance_id = data[0].get("id")
    
    with connection.cursor(dictionary=True) as cursor:
        query = """
                    SELECT * 
                    FROM compliance_integrations 
                    WHERE id = %s
                """
        cursor.execute(query, (compliance_id,))
        
        result = cursor.fetchall()
        
    
        refresh_token = ((json.loads((result[0]).get("response"))).get("data")).get("refresh_token")
        if not refresh_token:
            raise Exception("Refresh Token does not exist, contact client for auth code, client ID and client secret to generate refresh and access tokens")
        domain = ((json.loads((result[0]).get("response"))).get("data")).get("url")
        try:
            access_token = ((json.loads((result[0]).get("response"))).get("data")).get("access_token")
            if not access_token:
                return {"error": "'ZOHO_ACCESS_TOKEN' is not set in settings."}, 400
            
            if tool =="zoho":
                return fetch_and_save_zoho_asset_details(access_token, org_id, tool, domain, refresh_token,compliance_id)
            elif tool == "zohoHRM":
                return fetch_and_save_zoho_employee_details(access_token, org_id, tool, domain, refresh_token,compliance_id)
                
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

def fetch_and_save_zoho_asset_details(access_token, org_id,tool, domain, refresh_token, compliance_id):
    if not access_token:
        raise ValueError("Token not provided")
    zoho_api_url =f"{domain}/report/allmachines"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(zoho_api_url, headers=headers, timeout=10)
        if response.status_code == 401:
            refresh_response = refresh_zoho_access_token(
                refresh_token=refresh_token,
                client_id=getattr(settings, "ZOHO_CLIENT_ID", None),
                client_secret=getattr(settings, "ZOHO_CLIENT_SECRET", None),
                org_id=org_id,
                tool=tool,
                domain=domain,
                compliance_id=compliance_id    
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
                type = item.get("Type", {}).get("display_value", "") if item.get("Type") else None
                os = item.get("Operating_System", {}).get("display_value", "") if item.get("Operating_System") else None

                if warranty_info:
                    warranty_info = datetime.strptime(warranty_info, '%d-%b-%Y')

                filtered_hardware_data.append({
                    "org_id": org_id,
                    "inventory_number": inventory_number,
                    "warranty_info": warranty_info,
                    "serial_number": serial_number,
                    "purchase_date": purchase_date,
                    "name": name,
                    "type": type,
                    "operating_system": os,
                    "tool":tool
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


def fetch_and_save_zoho_employee_details(access_token, org_id,tool, domain, refresh_token, compliance_id):
    if not access_token:
        raise ValueError("Token not provided")
    # zoho_api_url =domain
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(domain, headers=headers, timeout=10)
        if response.status_code == 401:
            refresh_response = refresh_zoho_access_token(
                refresh_token=refresh_token,
                client_id=getattr(settings, "ZOHO_CLIENT_ID", None),
                client_secret=getattr(settings, "ZOHO_CLIENT_SECRET", None),
                org_id=org_id,
                tool=tool,
                domain=domain,
                compliance_id=compliance_id    
            )
            return JsonResponse(refresh_response, status=401)
        elif response.status_code == 200:
            data = response.json()
            filtered_employee_data = []
            
            for item in data:
                work_phone_number = item.get("Work Phone Number")
                permanent_address = item.get("Permanent Address")
                uan = item.get("UAN")
                email = item.get("Email address")
                first_name = item.get("First Name")
                emp_id = item.get("Employee ID")
                photo = item.get("Photo")
                added_by = item.get("Added By")
                source_of_hire = item.get("Source of Hire")
                gender = item.get("Gender")
                approval_status = item.get("ApprovalStatus")
                record_id = item.get("recordId")
                modified_by = item.get("Modified By")
                department = item.get("Department")
                seating_location = item.get("Seating Location")
                nick_name = item.get("Nick Name")
                employment_type = item.get("Employment Type")
                about_me = item.get("About Me")
                added_time = parseDate(item.get("Added Time", ""))
                zoho_role = item.get("Zoho Role")
                created_time = parseDate(item.get("createdTime", ""))
                current_address = item.get("Present Address")
                age = item.get("Age")
                tags = item.get("Tags")
                photo_download_url = item.get("Photo_downloadUrl")
                date_of_exit = parseDate(item.get("Date of Exit", ""))
                designation = item.get("Designation")
                ask_me_about_or_expertise = item.get("Ask me about/Expertise")
                employment_status = item.get("Employee Status")
                total_experience = item.get("Total Experience")
                aadhar = item.get("Aadhaar")
                current_experience = item.get("Current Experience")
                onboarding_status = item.get("Onboarding Status")
                personal_phone_number = item.get("Personal Mobile Number")
                owner_id = item.get("ownerID")
                marital_status = item.get("Marital Status")
                personal_email = item.get("Personal Email Address")
                modified_time = parseDate(item.get("Modified Time", ""))
                date_of_joining = parseDate(item.get("Date of Joining", ""))
                extension = item.get("Extension")
                reporting_manager = item.get("Reporting Manager")
                date_of_birth = parseDate(item.get("Date of Birth", ""))
                last_name = item.get("Last Name")
                pan_number = item.get("PAN")
                

                filtered_employee_data.append({
                    "org_id": org_id,
                    "work_phone_number": work_phone_number ,
                    "permanent_address" : permanent_address ,
                    "uan": uan ,
                    "email": email,
                    "first_name ": first_name ,
                    "emp_id ": emp_id ,
                    "photo ": photo ,
                    "added_by ":added_by ,
                    "source_of_hire ": source_of_hire ,
                    "gender ": gender ,
                    "approval_status": approval_status,
                    "record_id ": record_id ,
                    "modified_by": modified_by,
                    "department ": department ,
                    "seating_location ": seating_location ,
                    "nick_name ":nick_name ,
                    "employment_type ": employment_type ,
                    "about_me ": about_me ,
                    "added_time ": added_time ,
                    "zoho_role ": zoho_role ,
                    "created_time ": created_time ,
                    "current_address ":current_address ,
                    "age ": age ,
                    "tags ": tags ,
                    "photo_download_url ": photo_download_url ,
                    "date_of_exit ": date_of_exit ,
                    "designation ": designation ,
                    "ask_me_about_or_expertise": ask_me_about_or_expertise,
                    "employment_status ":employment_status ,
                    "total_experience" :total_experience,
                    "aadhar" :aadhar,
                    "current_experience" : current_experience,
                    "onboarding_status" :onboarding_status ,
                    "personal_phone_number" :personal_phone_number ,
                    "owner_id" : owner_id,
                    "marital_status" :marital_status,
                    "personal_email" : personal_email,
                    "modified_time" : modified_time,
                    "date_of_joining" : date_of_joining,
                    "extension" : extension,
                    "reporting_manager" : reporting_manager,
                    "date_of_birth" : date_of_birth,
                    "last_name" :last_name ,
                    "pan_number" : pan_number,
                    
                })
            
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGO_DB_NAME]
            collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_EMPLOYEES]
            
            new_count = 0
            updated_count = 0

            for item in filtered_employee_data:
                personal_email = item["personal_email"]
                if personal_email:
                    existing = collection.find_one({"personal_email": personal_email})
                    if existing:
                        if existing != item:
                            collection.update_one(
                                {"personal_email": personal_email},
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
                "total_objects": len(filtered_employee_data)
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

def parseDate(date_string):
    try:
        return datetime.strptime(date_string.strip(), "%Y-%m-%d").isoformat() if date_string.strip() else None
    except ValueError:
        return None