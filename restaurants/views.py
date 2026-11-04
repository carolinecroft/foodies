
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
    
    # Collect cuisines disliked by either user
    disliked_cuisines = {
        cuisine.strip().lower()
        for preferences in (preferences1, preferences2)
        for cuisine in preferences.disliked_cuisine.split(",")
        if cuisine.strip() and cuisine.strip().lower() != "none"
    }

    # Exclude restaurants explicitly categorized as a disliked cuisine
    restaurants = [
        restaurant
        for restaurant in restaurants
        if not any(
            disliked in restaurant["cuisine"].lower()
            for disliked in disliked_cuisines
        )
    ]
    
    # Collect dietary restrictions from both matched users
    dietary_restrictions = set()

    for preferences in (preferences1, preferences2):
        for restriction in preferences.dietary_restrictions.split(","):
            restriction = restriction.strip()

            if restriction and restriction.lower() != "none":
                dietary_restrictions.add(restriction)

    dietary_restrictions = sorted(dietary_restrictions)


    
    return render(request, "restaurants/match_recommendations.html", {
        "restaurants": restaurants,
        "match": match,
        "profile1": profile1,
        "profile2": profile2,
        "dietary_restrictions": dietary_restrictions,
    })

