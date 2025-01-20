import requests
from django.conf import settings
from pymongo import MongoClient
from django.http import JsonResponse
from datetime import datetime

def upkeep_main(organization_id, tool, body):
    url = "https://api.onupkeep.com/api/v2/auth"
    requestBody = {
        "email": body[0].get("email"),
        "password": body[0].get("password")
    }

    try:
        response = requests.post(url, json=requestBody)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to authenticate with UpKeep: {e}")
        return {"error": "Authentication failed with UpKeep"}, 500

    if response.status_code == 200:
        sessionToken = response.json().get("result", {}).get("sessionToken")
        if not sessionToken:
            return {"error": "Authentication succeeded but session token not found"}, 500
        assets = get_all_assets(sessionToken)
        return {"message": "Assets fetched and stored successfully", "assets": assets}, 200
    else:
        return {"error": "Failed to authenticate with UpKeep"}, response.status_code


def get_all_assets(sessionToken):
    url = "https://api.onupkeep.com/api/v2/assets"
    headers = {
        "Session-Token": sessionToken
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch assets from UpKeep: {e}")
        return []

    try:
        assets = response.json().get("results", [])
        if not assets:
            print("No assets returned from UpKeep API.")
            return []

        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_COLLECTION_NAME_FOR_ASSETS]

        new_assets = []
        for asset in assets:
            if not collection.find_one({"id": asset["id"]}):
                new_assets.append(asset)

        if new_assets:
            collection.insert_many(new_assets)
            print(f"{len(new_assets)} new assets stored successfully.")
        else:
            print("No new assets to store.")
    except Exception as e:
        print(f"Failed to process assets: {e}")
        return []
    finally:
        client.close()

    return assets
