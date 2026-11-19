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
from django.views.decorators.http import require_http_methods




@login_required
def discovery(request):

    current_profile = Profile.objects.filter(
        user=request.user
    ).first()

    if current_profile is None:
        return redirect("profile_setup")

    preferred_genders = current_profile.interested_in or []

    # Exclude users already liked or passed
    interacted_user_ids = Interaction.objects.filter(
        actor=request.user
    ).values_list("target_id", flat=True)

    # Exclude existing matches
    matched_user_ids = set()

    user_matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )

    for match in user_matches:
        if match.user1_id == request.user.pk:
            matched_user_ids.add(match.user2_id)
        else:
            matched_user_ids.add(match.user1_id)

    # Retrieve eligible profiles
    profiles = Profile.objects.exclude(
        user=request.user
    ).exclude(
        user_id__in=interacted_user_ids
    ).exclude(
        user_id__in=matched_user_ids
    ).filter(
        gender__in=preferred_genders
    ).select_related("user").order_by("pk")

    candidates = []

    for profile in profiles:

        # Check mutual gender preferences
        their_preferences = profile.interested_in or []

        if current_profile.gender not in their_preferences:
            continue

        # Retrieve candidate food preferences
        food_preferences = FoodPreferences.objects.filter(
            profile=profile
        ).first()

        # Use existing compatibility service
        compatibility_result = calculate_food_compatibility(
            request.user,
            profile.user
        )

        # Extract the numeric score
        compatibility_score = compatibility_result["score"]

        candidates.append({
            "profile": profile,
            "food_preferences": food_preferences,
            "compatibility_score": compatibility_score,
        })

    # Sort scored candidates from highest to lowest
    # Missing scores appear last
    # Profile ID breaks ties consistently
    candidates.sort(
        key=lambda candidate: (
            candidate["compatibility_score"] is None,
            -candidate["compatibility_score"]
            if candidate["compatibility_score"] is not None
            else 0,
            candidate["profile"].pk
        )
    )

    context = {
        "candidates": candidates,
    }

    return render(request, "discover.html", context)

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
@require_http_methods(["GET", "POST"])
def compatibility(request, profile_id=None):
    responded_user_ids = Interaction.objects.filter(
        actor=request.user
    ).values_list("target_id", flat=True)

    incoming_likes = (
        Interaction.objects.filter(
            target = request.user,
            action = Interaction.LIKE
        )
        .exclude(actor_id__in=responded_user_ids)
        .select_related("actor__profile")
        .order_by("created_at")
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action not in (Interaction.LIKE, Interaction.PASS):
            return redirect('compatibility')

        incoming_like = get_object_or_404(
            incoming_likes,
            pk = request.POST.get("interaction_id")
        )

        try:
            record_interaction(
                actor = request.user,
                target = incoming_like.actor,
                action = action,
            )

        except ValidationError:
            pass

        return redirect('Liked_You')

    return render(request, 'matching/Liked_You.html', {
        "incoming_likes": incoming_likes,
        })