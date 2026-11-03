
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import search_restaurants


@login_required
def restaurant_list(request):
    restaurants = search_restaurants()

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })
