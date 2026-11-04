
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from accounts.models import Profile, FoodPreferences
from matching.models import Match
from .services import search_restaurants


@login_required
def restaurant_list(request):
    restaurants = search_restaurants()

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })


@login_required
def match_recommendations(request, match_id):
    # Retrieve the requested match
    match = get_object_or_404(Match, id=match_id)

    # Only members of the match can view recommendations
    if request.user.id not in (match.user1_id, match.user2_id):
        return HttpResponseForbidden("You cannot view this match.")

    # Get both users' profiles and preferences
    profile1 = get_object_or_404(Profile, user=match.user1)
    profile2 = get_object_or_404(Profile, user=match.user2)

    preferences1 = get_object_or_404(FoodPreferences, profile=profile1)
    preferences2 = get_object_or_404(FoodPreferences, profile=profile2)

    # Determine cuisine preferences
    cuisine1 = preferences1.favorite_cuisine.strip()
    cuisine2 = preferences2.favorite_cuisine.strip()

    if cuisine1.lower() == cuisine2.lower():
        cuisine = cuisine1
    else:
        cuisine = f"{cuisine1} or {cuisine2}"

    # Use the current user's location for searching
    location = (
        profile1.location
        if request.user == match.user1
        else profile2.location
    )

    query = f"{cuisine} restaurants in {location}"
    restaurants = search_restaurants(query)
    
    # Prioritize restaurants matching both users' price preferences
    price1 = preferences1.preferred_price_range
    price2 = preferences2.preferred_price_range

    if price1 == price2:
        preferred_price = price1

        restaurants = sorted(
            restaurants,
            key=lambda restaurant: (
                restaurant["price_range"] != preferred_price
            )
        )

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })
