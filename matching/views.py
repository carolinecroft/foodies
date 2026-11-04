from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Match


@login_required
def discovery(request):
    return render(request, 'matching/discovery.html')


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
def compatibility(request):
    return render(request, 'matching/compatibility.html')
