from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path(
        'recommendations/<int:match_id>/',
        views.match_recommendations,
        name='match_restaurant_recommendations',
    ),
]