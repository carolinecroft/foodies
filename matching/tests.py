from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, SimpleTestCase

from accounts.models import FoodPreferences
from .models import Interaction, Match
from .services import record_interaction, score_food_preferences


User = get_user_model()


# Like/Pass and Mutual Matching Tests

class MatchingTests(TestCase):

    def setUp(self):
        # Create two sample users for each test
        self.alice = User.objects.create_user(
            email="alice@example.com",
            password="testpassword123",
        )

        self.bob = User.objects.create_user(
            email="bob@example.com",
            password="testpassword123",
        )

    def test_single_like_does_not_create_match(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)

        self.assertEqual(Interaction.objects.count(), 1)
        self.assertEqual(Match.objects.count(), 0)

    def test_mutual_likes_create_one_match(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)
        record_interaction(self.bob, self.alice, Interaction.LIKE)

        self.assertEqual(Interaction.objects.count(), 2)
        self.assertEqual(Match.objects.count(), 1)

        match = Match.objects.first()

        self.assertEqual(
            {match.user1, match.user2},
            {self.alice, self.bob},
        )

    def test_pass_does_not_create_match(self):
        record_interaction(self.alice, self.bob, Interaction.PASS)
        record_interaction(self.bob, self.alice, Interaction.LIKE)

        self.assertEqual(Match.objects.count(), 0)

    def test_cannot_interact_with_self(self):
        with self.assertRaises(ValidationError):
            record_interaction(
                self.alice,
                self.alice,
                Interaction.LIKE,
            )

        self.assertEqual(Interaction.objects.count(), 0)

    def test_duplicate_interaction_rejected(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)

        with self.assertRaises(ValidationError):
            record_interaction(
                self.alice,
                self.bob,
                Interaction.LIKE,
            )

        self.assertEqual(Interaction.objects.count(), 1)
        self.assertEqual(Match.objects.count(), 0)

    def test_invalid_action_rejected(self):
        with self.assertRaises(ValidationError):
            record_interaction(
                self.alice,
                self.bob,
                "maybe",
            )

        self.assertEqual(Interaction.objects.count(), 0)

    def test_duplicate_match_rejected(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)
        record_interaction(self.bob, self.alice, Interaction.LIKE)

        match = Match.objects.first()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Match.objects.create(
                    user1=match.user1,
                    user2=match.user2,
                )

        self.assertEqual(Match.objects.count(), 1)

    def test_reversed_match_rejected(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)
        record_interaction(self.bob, self.alice, Interaction.LIKE)

        match = Match.objects.first()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Match.objects.create(
                    user1=match.user2,
                    user2=match.user1,
                )

        self.assertEqual(Match.objects.count(), 1)

    def test_duplicate_like_after_match(self):
        record_interaction(self.alice, self.bob, Interaction.LIKE)
        record_interaction(self.bob, self.alice, Interaction.LIKE)

        with self.assertRaises(ValidationError):
            record_interaction(
                self.alice,
                self.bob,
                Interaction.LIKE,
            )

        self.assertEqual(Interaction.objects.count(), 2)
        self.assertEqual(Match.objects.count(), 1)


# Food Compatibility Tests

class FoodCompatibilityTest(SimpleTestCase):

    def make_preferences(self, **overrides):
        values = {
            "favorite_cuisine": "Italian",
            "disliked_cuisine": "",
            "dietary_restrictions": "",
            "favorite_food": "Pizza",
            "preferred_price_range": "$$",
            "preferred_dining_atmosphere": "Casual",
            "willing_to_try_new_foods": True,
        }
        values.update(overrides)
        return FoodPreferences(**values)

    def test_matching_preference_score_100(self):
        first = self.make_preferences()
        second = self.make_preferences()
        result = score_food_preferences(first, second)

        self.assertEqual(result["score"], 100)
        self.assertIsNone(result["reason"])
        self.assertEqual(len(result["breakdown"]), 5)
        self.assertTrue(
            all(item["matched"] for item in result["breakdown"].values())
        )

    def test_matching_preference_score_0(self):
        first = self.make_preferences()
        second = self.make_preferences(
            favorite_cuisine="Japanese",
            favorite_food="Sushi",
            preferred_price_range="$$$",
            preferred_dining_atmosphere="Quiet",
            willing_to_try_new_foods=False,
        )

        result = score_food_preferences(first, second)
        self.assertEqual(result["score"], 0)

    def test_price_and_atmosphere_mismatch(self):
        first = self.make_preferences()
        second = self.make_preferences(
            preferred_price_range="$$$",
            preferred_dining_atmosphere="Quiet",
        )

        result = score_food_preferences(first, second)
        self.assertEqual(result["score"], 60)
        self.assertFalse(
            result["breakdown"]["preferred_price_range"]["matched"]
        )
        self.assertFalse(
            result["breakdown"]["preferred_dining_atmosphere"]["matched"]
        )

    def test_missing_preferences(self):
        preferences = self.make_preferences()

        for first, second in (
            (preferences, None),
            (None, preferences),
            (None, None),
        ):
            with self.subTest(first=first, second=second):
                result = score_food_preferences(first, second)
                self.assertIsNone(result["score"])
                self.assertTrue(result["reason"])
                self.assertEqual(result["breakdown"], {})

    def test_blank_optional_fields(self):
        first = self.make_preferences(favorite_food="")
        second = self.make_preferences()

        result = score_food_preferences(first, second)
        self.assertEqual(result["score"], 100)
        self.assertNotIn("favorite_food", result["breakdown"])

    def test_false_is_a_valid_answer(self):
        first = self.make_preferences(willing_to_try_new_foods=False)
        second = self.make_preferences(willing_to_try_new_foods=False)

        result = score_food_preferences(first, second)
        self.assertEqual(result["score"], 100)
        self.assertTrue(
            result["breakdown"]["willing_to_try_new_foods"]["matched"]
        )

    def test_no_compareable_fields(self):
        first = self.make_preferences(
            favorite_cuisine="",
            favorite_food="",
            preferred_price_range="",
            preferred_dining_atmosphere="",
            willing_to_try_new_foods=None,
        )
        second = self.make_preferences()

        result = score_food_preferences(first, second)
        self.assertIsNone(result["score"])
        self.assertTrue(result["reason"])
        self.assertEqual(result["breakdown"], {})

    def test_cuisine_conflict(self):
        first = self.make_preferences()
        second = self.make_preferences(
            favorite_cuisine="Japanese",
            disliked_cuisine="Italian",
        )

        result = score_food_preferences(first, second)
        reversed_result = score_food_preferences(second, first)

        self.assertEqual(result["score"], 50)
        self.assertEqual(result["cuisine_conflicts"], 1)
        self.assertEqual(result, reversed_result)
