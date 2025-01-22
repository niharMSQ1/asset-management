import requests
from django.conf import settings
from pymongo import MongoClient

def connect_team_main(org_id, tool, body):
    base_url = "https://api.connecteam.com/users/v1/users"
    api_key = (body[0])["connnect_team_api_key"]

    if not api_key:
        return {"error": "API key is missing in the request body."}, 400

    headers = {
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    limit = 500
    offset = 0
    all_users = []

    try:
        while True:
            url = f"{base_url}?limit={limit}&offset={offset}&order=asc&userStatus=active"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                return {
                    "error": "Failed to fetch data from Connecteam API.",
                    "status_code": response.status_code,
                    "details": response.json() if response.headers.get("Content-Type") == "application/json" else response.text
                }, response.status_code

            data = response.json()
            users = data.get("data", {}).get("users", [])
            all_users.extend(users)

            # If the number of users fetched is less than the limit, stop pagination
            if len(users) < limit:
                break

            offset += limit

        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS_FOR_EMPLOYEES]

        new_all_users = []
        for user in all_users:
            if not collection.find_one({"id": user.get("userId")}):
                new_all_users.append(user)

        if new_all_users:
            collection.insert_many(new_all_users)

        return {
            "total_users": len(all_users),
            "message": "Users saved added successfully."
        }, 200

    except requests.exceptions.RequestException as e:
        return {
            "error": "An error occurred while making the request to Connecteam API.",
            "details": str(e)
        }, 500

    except Exception as e:
        return {
            "error": "An unexpected error occurred.",
            "details": str(e)
        }, 500
