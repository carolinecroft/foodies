from accounts.models import FoodPreferences

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
    avaliable_weight = 0
    breakdown = {}

    for field, weight in WEIGHTED_FIELDS:
        first_value = normalize(getattr(first, field))
        second_value = normalize(getattr(second, field))

        if first_value in (None, "") or second_value in (None, ""):
            continue

        matched = first_value == second_value
        avaliable_weight += weight

        if matched:
            earned_weight += weight

        breakdown[field] = {
            "matched": matched,
            "weight": weight,
        }

    if avaliable_weight == 0:
        return {
            "score": None,
            "reason": "Not enough data to calculate a score",
            "breakdown": breakdown,
            "cuisine_conflicts": 0,
        }

    cuisine_conflicts = 0

    for person, other in ((first, second)), ((second, first)):
        favorite = normalize(person.favorite_cuisine)
        disliked = normalize(person.disliked_cuisine)

        if favorite and disliked and favorite == disliked:
            cuisine_conflicts += 1

    base_score = earned_weight / avaliable_weight * 100
    final_score = max(0, min(100, base_score - (cuisine_conflicts * 15))) 

    return {
        "score": round(final_score),
        "reason": None,
        "breakdown": breakdown,
        "cuisine_conflicts": cuisine_conflicts,
    }

def calculate_food_compatibility(user1, user2):
    preferences = {
        preferences.profile.user.id: preferences
        for preferences in FoodPreferences.objects.filter(
            profile__user_id__in=[user1.pk, user2.pk]
        ).select_related("profile")
    }

    return score_food_preferences(
        preferences.get(user1.pk), 
        preferences.get(user2.pk)
    )