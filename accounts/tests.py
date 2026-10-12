from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Profile, FoodPreferences


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
        
    def test_food_preferences_save_correctly(self):
        User = get_user_model()

        user = User.objects.create_user(
            email="foodtest@example.com",
            password="testpassword123"
        )

        profile = Profile.objects.create(
            user=user,
            name="Food Test",
            age=21,
            gender="F",
            location="Lakeland"
        )

        FoodPreferences.objects.create(
            profile=profile,
            favorite_cuisine="Italian",
            preferred_price_range="Moderate",
            preferred_dining_atmosphere="Casual",
            willing_to_try_new_foods=True
        )

        saved_preferences = FoodPreferences.objects.get(profile=profile)

        self.assertEqual(saved_preferences.favorite_cuisine, "Italian")
        self.assertEqual(saved_preferences.preferred_price_range, "Moderate")
        self.assertEqual(saved_preferences.preferred_dining_atmosphere, "Casual")
        self.assertTrue(saved_preferences.willing_to_try_new_foods)