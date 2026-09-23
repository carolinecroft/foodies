from django.urls import path
from . import views

urlpatterns = [
    path("food-preferences/", views.food_preferences, name="food_preferences"),
]