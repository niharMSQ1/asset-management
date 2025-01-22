import requests
from django.conf import settings
from pymongo import MongoClient
'''
url = "https://subdomain.workable.com/spi/v3/employees?limit=10&offset=0"

'''
def workableMain(org_id, tool, body):
    base_url = (body[0]).get("url") + "/spi/v3/employees"
    access_token = (body[0]).get("access_token")

    if not base_url or not access_token:
        return {"error": "URL or access token is missing in the request body."}, 400

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    limit = 10
    offset = 0
    all_employees = []

    try:
        while True:
            url = f"{base_url}?limit={limit}&offset={offset}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {
                    "error": "Failed to fetch data from Workable API.",
                    "status_code": response.status_code,
                    "details": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
                }, response.status_code

            data = response.json()
            employees = data.get("employees", [])
            all_employees.extend(employees)

            if len(employees) < limit:
                break

            offset += limit

        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_EMPLOYEES]

        new_employees = []
        for employee in all_employees:
            if not collection.find_one({"id": employee.get("id")}):
                new_employees.append(employee)

        if new_employees:
            collection.insert_many(new_employees)

        return {
            "total_users": len(all_employees),
            "message": "Users saved and added successfully."
        }, 200

    except requests.exceptions.RequestException as e:
        return {
            "error": "An error occurred while making the request to Workable API.",
            "details": str(e)
        }, 500

    except Exception as e:
        return {
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, 500
