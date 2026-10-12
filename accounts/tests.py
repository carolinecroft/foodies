from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Profile


class AccountTests(TestCase):

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
        

    def test_profile_saves_correctly(self):
        User = get_user_model()

        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123"
        )

        profile = Profile.objects.create(
            user=user,
            name="Test User",
            age=21,
            gender="F",
            location="Lakeland"
        )

        saved_profile = Profile.objects.get(user=user)

        self.assertEqual(saved_profile.name, "Test User")
        self.assertEqual(saved_profile.age, 21)
        self.assertEqual(saved_profile.location, "Lakeland")