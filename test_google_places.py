
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

url = "https://places.googleapis.com/v1/places:searchText"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": os.getenv("GOOGLE_PLACES_API_KEY"),
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress",
}

data = {
    "textQuery": "Italian restaurants in Lakeland Florida",
    "pageSize": 5,
}

response = requests.post(url, headers=headers, json=data, timeout=10)

print("Status:", response.status_code)

if response.status_code == 200:
    for place in response.json().get("places", []):
        print(place["displayName"]["text"])
        print(place.get("formattedAddress", "No address"))
        print()
else:
    print(response.text)
