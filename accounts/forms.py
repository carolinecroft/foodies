from django import forms
from .models import Profile, FoodPreferences


CUISINE_CHOICES = [
    ("Asian", [
        ("Chinese", "Chinese"),
        ("Japanese", "Japanese"),
        ("Korean", "Korean"),
        ("Thai", "Thai"),
        ("Indian", "Indian"),
        ("Vietnamese", "Vietnamese"),
    ]),
    ("African", [
        ("Ethiopian", "Ethiopian"),
        ("Nigerian", "Nigerian"),
        ("Ghanaian", "Ghanaian"),
        ("Moroccan", "Moroccan"),
    ]),
    ("Caribbean", [
        ("Jamaican", "Jamaican"),
        ("Haitian", "Haitian"),
        ("Trinidadian", "Trinidadian"),
        ("Cuban", "Cuban"),
    ]),
    ("European", [
        ("Italian", "Italian"),
        ("French", "French"),
        ("Greek", "Greek"),
        ("Spanish", "Spanish"),
    ]),
    ("The Americas", [
        ("American", "American"),
        ("Mexican", "Mexican"),
        ("Brazilian", "Brazilian"),
        ("Peruvian", "Peruvian"),
    ]),
    ("Middle Eastern & Mediterranean", [
        ("Lebanese", "Lebanese"),
        ("Turkish", "Turkish"),
        ("Persian", "Persian"),
        ("Mediterranean", "Mediterranean"),
    ]),
]



class ProfileForm(forms.ModelForm):
    interested_in = forms.MultipleChoiceField(
        choices=Profile._meta.get_field("gender").choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Interested in",
    )


    class Meta:
        model = Profile
        fields = [
            "name",
            "age",
            "gender",
            "bio",
            "location",
            "interested_in",
            "distance_preference",
            "profile_prompt",
        ]

        labels = {
            "name": "Display name",
            "distance_preference": "Maximum distance (miles)",
            "profile_prompt": "What would your ideal first date look like?",
        }

        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "profile_prompt": forms.Textarea(attrs={"rows": 3}),
        }


class FoodPreferencesForm(forms.ModelForm):
    favorite_cuisine = forms.ChoiceField(
        choices=[("", "Select a cuisine")] + CUISINE_CHOICES,
        required=True,
    )

    disliked_cuisine = forms.ChoiceField(
        choices=[("", "None")] + CUISINE_CHOICES,
        required=False,
    )

    preferred_price_range = forms.ChoiceField(
        choices=[
            ("", "Select a price range"),
            ("$", "$"),
            ("$$", "$$"),
            ("$$$", "$$$"),
        ],
        required=True,
    )

    preferred_dining_atmosphere = forms.ChoiceField(
        choices=[
            ("", "Select an atmosphere"),
            ("Casual", "Casual"),
            ("Quiet", "Quiet"),
            ("Social", "Social"),
        ],
        required=True,
    )

    willing_to_try_new_foods = forms.TypedChoiceField(
        choices=[
            ("True", "Yes"),
            ("False", "No"),
        ],
        coerce=lambda value: value == "True",
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = FoodPreferences
        fields = [
            "favorite_cuisine",
            "disliked_cuisine",
            "dietary_restrictions",
            "favorite_food",
            "preferred_price_range",
            "preferred_dining_atmosphere",
            "willing_to_try_new_foods",
        ]
