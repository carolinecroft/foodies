# Profile Contract — Sprint 2

Model: Profile in accounts/models.py
Form: ProfileForm in accounts/forms.py

## Fields

- name: required, max 100 characters
- age: required, 18 or older
- gender: required, M / F / O
- bio: optional
- location: required, max 100 characters
- interested_in: at least one selection; stored as a list of M / F / O
- distance_preference: at least 1 mile; default 25
- profile_prompt: optional, max 300 characters

M = Male, F = Female, O = Other.

The view assigns user from request.user, not from form input.

## Create and edit

Both use /profile/setup/ with route name profile_setup.

- Login is required.
- Existing information is prefilled.
- Saving updates the same profile.
- Successful saves redirect to food_preferences.
- Invalid entries show errors without changing saved data.

## Team integration

Kei:
- Link FoodPreferences to the current user's Profile.
- Redirect to profile_setup if their profile is missing.

Shyanne:
- Display the current user's Profile and FoodPreferences.
- Use profile_setup for the Edit Profile link.
- Handle missing records and optional fields.

Photo uploading is deferred.

## Testing

Manual checks passed for saving, editing, validation,
separate profiles, and persistence through admin logout/login.

Automated tests, app authentication integration,
team confirmation, and PR review remain pending.