from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def restaurant_list(request):
    restaurants = [
    {
        'name': 'Olive Garden',
        'cuisine': 'Italian',
        'location': 'Lakeland, FL',
        'price_range': '$$',
        'website': 'https://www.olivegarden.com/',
        'maps_url': 'https://www.google.com/maps/search/?api=1&query=Olive+Garden+Lakeland+FL',
    },
    {
        'name': 'Texas Roadhouse',
        'cuisine': 'American',
        'location': 'Lakeland, FL',
        'price_range': '$$',
        'website': 'https://www.texasroadhouse.com/',
        'maps_url': 'https://www.google.com/maps/search/?api=1&query=Texas+Roadhouse+Lakeland+FL',
    },
    {
        'name': 'Sushi Masa',
        'cuisine': 'Japanese',
        'location': 'Lakeland, FL',
        'price_range': '$$',
        'website': 'https://sushimasaus.com/sushi-masa-lakeland.html',
        'maps_url': 'https://www.google.com/maps/search/?api=1&query=Sushi+Masa+Lakeland+FL',
    },
]

    return render(request, 'restaurants/restaurant_list.html', {
        'restaurants': restaurants
    })