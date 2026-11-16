from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.views.decorators.http import require_POST

from accounts.models import Profile, FoodPreferences
from .services import calculate_food_compatibility, record_interaction
from django.core.exceptions import ValidationError
from .models import Match, Interaction

from django.contrib import messages
from django.core.exceptions import ValidationError
from .services import calculate_food_compatibility, record_interaction


@login_required
def discovery(request):

    interacted_user_ids = Interaction.objects.filter(
        actor=request.user
    ).values_list("target_id", flat=True)

    matched_user_ids = set()

    user_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    for match in user_matches:
        if match.user1_id == request.user.pk:
            matched_user_ids.add(match.user2_id)
        else:
            matched_user_ids.add(match.user1_id)

    profiles = Profile.objects.exclude(
        user=request.user
    ).exclude(
        user_id__in=interacted_user_ids
    ).exclude(
        user_id__in=matched_user_ids
    ).select_related("user").order_by("pk")

    candidates = []

    for profile in profiles:

        food_preferences = FoodPreferences.objects.filter(
            profile=profile
        ).first()

        candidates.append({
            "profile" : profile,
            "food_preferences" : food_preferences,
        })

    context = {
        "candidates" : candidates,
    }

    return render(request, 'discover.html', context)

@login_required
@require_POST
def interact(request, profile_id):
    target_profile = get_object_or_404(Profile, pk=profile_id)

    action = request.POST.get("action")

    try:
        record_interaction(
            request.user,
            target_profile.user,
            action
        )
    except ValidationError as error:
        messages.error(request, "; ".join(error.messages))

    return redirect("discover")


@login_required
def matches(request):
    # Find matches involving the logged-in user
    user_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).select_related("user1", "user2").order_by("-created_at")

    # Identify the other user in each match
    matches_with_users = []

    for match in user_matches:
        other_user = (
            match.user2
            if match.user1_id == request.user.pk
            else match.user1
        )

        matches_with_users.append({
            "match": match,
            "other_user": other_user,
        })

    return render(request, 'matching/matches.html', {
        "matches": matches_with_users,
    })


@login_required
def match_detail(request, match_id):
    # Only allow users to view their own matches
    match = get_object_or_404(
        Match.objects.select_related("user1", "user2").filter(
            Q(user1=request.user) | Q(user2=request.user)
        ),
        pk=match_id,
    )

    # Find the other person in the match
    other_user = (
        match.user2
        if match.user1_id == request.user.pk
        else match.user1
    )

    return render(request, 'matching/match_detail.html', {
        "match": match,
        "other_user": other_user,
    })


@login_required
def compatibility(request, profile_id=None):
    profiles = (
        Profile.objects.exclude(user=request.user)
        .select_related("user")
    )

    other_profile = None
    result = None

    if profile_id is not None:
        other_profile = get_object_or_404(profiles, pk=profile_id)
        result = calculate_food_compatibility(request.user, other_profile.user)
   
    return render(request, 'matching/compatibility.html', {
        "profiles": profiles,
        "other_profile": other_profile,
        "result": result,
    })
