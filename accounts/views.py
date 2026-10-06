from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm
from .models import Profile

def home(request):
    return render(request, "home.html")


def food_preferences(request):
    return render(request, "food_preferences.html")


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


def profile(request):
    return render(request, "profile.html")