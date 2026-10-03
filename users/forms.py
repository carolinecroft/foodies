from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def clean_email(self):
        email = User.objects.normalize_email(
            self.cleaned_data["email"]
        )

        if User.objects.filter(email_iexact=email).exists():
            raise forms.ValidationError(
                "A user with that email already exists."
            )

        return email