from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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
        
    def test_users_have_separate_profiles(self):
        User = get_user_model()

        user1 = User.objects.create_user(
            email="user1@example.com",
            password="testpassword123"
        )

        user2 = User.objects.create_user(
            email="user2@example.com",
            password="testpassword123"
        )

        Profile.objects.create(
            user=user1,
            name="User One",
            age=21,
            gender="F",
            location="Lakeland"
        )

        Profile.objects.create(
            user=user2,
            name="User Two",
            age=22,
            gender="M",
            location="Tampa"
        )

        self.client.force_login(user1)
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["profile_setup"].name,
            "User One"
        )

    def test_profile_rejects_underage_user(self):
        User = get_user_model()

        user = User.objects.create_user(
            email="underage@example.com",
            password="testpassword123"
        )

        profile = Profile(
            user=user,
            name="Underage Test",
            age=17,
            gender="F",
            location="Lakeland"
        )

        with self.assertRaises(ValidationError):
            profile.full_clean()


class AppearanceSettingsTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="appearance@example.com",
            password="testpassword123"
        )

        self.profile = Profile.objects.create(
            user=self.user,
            name="Appearance Test",
            age=21,
            gender="F",
            location="Lakeland"
        )

        self.url = reverse("appearance_settings")

    def test_default_theme_is_light(self):
        self.assertEqual(self.profile.theme, "light")

    def test_appearance_page_requires_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_appearance_page_loads(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_theme"],
            "light"
        )

    def test_user_can_save_dark_mode(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"theme": "dark"}
        )

        self.assertRedirects(response, self.url)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, "dark")

    def test_user_can_switch_back_to_light_mode(self):
        self.profile.theme = "dark"
        self.profile.save()

        self.client.force_login(self.user)

        self.client.post(
            self.url,
            {"theme": "light"}
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, "light")

    def test_invalid_theme_is_not_saved(self):
        self.client.force_login(self.user)

        self.client.post(
            self.url,
            {"theme": "invalid"}
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.theme, "light")

    def test_theme_persists_after_logout_and_login(self):
        self.client.force_login(self.user)

        self.client.post(
            self.url,
            {"theme": "dark"}
        )

        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["selected_theme"],
            "dark"
        )

    def test_users_have_independent_themes(self):
        User = get_user_model()

        other_user = User.objects.create_user(
            email="otherappearance@example.com",
            password="testpassword123"
        )

        other_profile = Profile.objects.create(
            user=other_user,
            name="Other User",
            age=22,
            gender="M",
            location="Tampa"
        )

        self.client.force_login(self.user)

        self.client.post(
            self.url,
            {"theme": "dark"}
        )

        self.profile.refresh_from_db()
        other_profile.refresh_from_db()

        self.assertEqual(self.profile.theme, "dark")
        self.assertEqual(other_profile.theme, "light")

        self.client.force_login(other_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.context["selected_theme"],
            "light"
        )

    def test_dark_theme_applies_to_base_template(self):
        self.profile.theme = "dark"
        self.profile.save()

        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            'data-theme="dark"'
        )
