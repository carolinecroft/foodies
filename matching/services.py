from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import FoodPreferences
from .models import Interaction, Match


# Like/Pass Interactions and Mutual Matching

@transaction.atomic
def record_interaction(actor, target, action):
    # Make sure the action is valid
    if action not in [Interaction.LIKE, Interaction.PASS]:
        raise ValidationError("Action must be 'like' or 'pass'.")

    # Users cannot like or pass themselves
    if actor.pk == target.pk:
        raise ValidationError("You cannot interact with yourself.")

    # Prevent duplicate interactions
    if Interaction.objects.filter(actor=actor, target=target).exists():
        raise ValidationError("You have already interacted with this user.")

    # Save the interaction
    interaction = Interaction.objects.create(
        actor=actor,
        target=target,
        action=action,
    )

    # Only likes can create matches
    if action == Interaction.LIKE:
        # Check whether the other user already liked this user
        reciprocal_like = Interaction.objects.filter(
            actor=target,
            target=actor,
            action=Interaction.LIKE,
        ).exists()

        if reciprocal_like:
            # Always store the smaller user ID first
            user1, user2 = sorted(
                [actor, target],
                key=lambda user: user.pk,
            )

            # Create a match only if one does not already exist
            Match.objects.get_or_create(
                user1=user1,
                user2=user2,
            )

    return interaction


# Food Compatibility Scoring

WEIGHTED_FIELDS = (
    ("favorite_cuisine", 35),
    ("preferred_price_range", 20),
    ("preferred_dining_atmosphere", 20),
    ("willing_to_try_new_foods", 15),
    ("favorite_food", 10),
)


def normalize(value):
    if isinstance(value, str):
        return value.strip().casefold()
    return value


def score_food_preferences(first, second):
    if first is None or second is None:
        return {
            "score": None,
            "reason": "Both users must have a saved FoodPreferences instance",
            "breakdown": {},
            "cuisine_conflicts": 0,
        }

    earned_weight = 0
    available_weight = 0
    breakdown = {}

    for field, weight in WEIGHTED_FIELDS:
        first_value = normalize(getattr(first, field))
        second_value = normalize(getattr(second, field))

        if first_value in (None, "") or second_value in (None, ""):
            continue

        matched = first_value == second_value
        available_weight += weight

        if matched:
            earned_weight += weight

        breakdown[field] = {
            "matched": matched,
            "weight": weight,
        }

    if available_weight == 0:
        return {
            "score": None,
            "reason": "Not enough data to calculate a score",
            "breakdown": breakdown,
            "cuisine_conflicts": 0,
        }

    cuisine_conflicts = 0

    for person, other in ((first, second), (second, first)):
        favorite = normalize(person.favorite_cuisine)
        disliked = normalize(other.disliked_cuisine)

        if favorite and disliked and favorite == disliked:
            cuisine_conflicts += 1

    base_score = earned_weight / available_weight * 100
    final_score = max(
        0,
        min(100, base_score - (cuisine_conflicts * 15)),
    )

    return {
        "score": round(final_score),
        "reason": None,
        "breakdown": breakdown,
        "cuisine_conflicts": cuisine_conflicts,
    }


def calculate_food_compatibility(user1, user2):
    preferences = {
        preference.profile.user_id: preference
        for preference in FoodPreferences.objects.filter(
            profile__user_id__in=[user1.pk, user2.pk]
        ).select_related("profile")
    }

    return score_food_preferences(
        preferences.get(user1.pk),
        preferences.get(user2.pk),
    )
