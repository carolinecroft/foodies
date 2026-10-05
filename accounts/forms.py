from django import forms
from .models import Profile


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