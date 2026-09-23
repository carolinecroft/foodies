from django.shortcuts import render


def home(request):
    return render(request, "home.html")


def food_preferences(request):
    return render(request, "food_preferences.html")