
import logging

import requests
from django.conf import settings
from django.core.cache import cache
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def search_restaurants(query="restaurants in Lakeland Florida"):
    """Get restaurant information from Google Places API."""

    cache_key = "places_search:" + query
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress",
    }

    data = {
        "textQuery": query,
        "includedType": "restaurant",
        "strictTypeFiltering": True,
        "pageSize": 10,
    }

    try:
        response = requests.post(
            url, headers=headers, json=data, timeout=10
        )
        response.raise_for_status()

        restaurants = []

        for place in response.json().get("places", []):
            name = place.get("displayName", {}).get("text", "")
            address = place.get("formattedAddress", "")

            restaurants.append({
                "name": name,
                "location": address,
                "cuisine": "Restaurant",
                "price_range": "Not available",
                "website": None,
                "maps_url": (
                    "https://www.google.com/maps/search/?api=1&query="
                    + quote_plus(name + " " + address)
                ),
            })

        cache.set(cache_key, restaurants, 900)
        return restaurants

    except (requests.RequestException, ValueError):
        logger.exception("Google Places restaurant search failed")
        return []
