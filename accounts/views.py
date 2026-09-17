from django.shortcuts import render

def home(request):
    return render(request, "home.html")
# Create your views here.

def profile_setup(request):
    return render(request, "profile_setup.html")