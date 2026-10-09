from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm, FoodPreferencesForm
from .models import Profile, FoodPreferences

def home(request):
    return render(request, "home.html")


@login_required
def food_preferences(request):
    # Get the profile belonging to the logged-in user
    user_profile = Profile.objects.filter(user=request.user).first()

    # If they don't have a profile, send them to setup
    if user_profile is None:
        return redirect("profile_setup")

    # Find their previously saved food preferences
    preferences = FoodPreferences.objects.filter(
        profile=user_profile
    ).first()

    if request.method == "POST":
        # Use existing preferences if they already have some
        form = FoodPreferencesForm(
            request.POST,
            instance=preferences
        )

        if form.is_valid():
            saved_preferences = form.save(commit=False)
            saved_preferences.profile = user_profile
            saved_preferences.save()

            return redirect("food_preferences")

    else:
        # Show saved values when returning to the page
        form = FoodPreferencesForm(instance=preferences)

    return render(
        request,
        "food_preferences.html",
        {"form": form},
    )



# Create your views here.

@login_required
def profile_setup(request):
    existing_profile = Profile.objects.filter(
        user=request.user
    ).first()

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            instance=existing_profile,
        )

        if form.is_valid():
            saved_profile = form.save(commit=False)
            saved_profile.user = request.user
            saved_profile.save()

            return redirect("food_preferences")
    else:
        form = ProfileForm(instance=existing_profile)

    return render(
        request,
        "profile_setup.html",
        {"form": form},
    )

@login_required
def profile(request):

    user_profile = Profile.objects.filter(
        user=request.user
    ).first()

    preferences = FoodPreferences.objects.filter(
        profile=user_profile
    ).first()

    context = {
        "profile_setup": user_profile,
        "food_preferences": preferences
    }

    return render(request, "profile.html", context)