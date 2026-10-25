from django.test import SimpleTestCase
from accounts.models import FoodPreferences
from matching.services import score_food_preferences

class FoodCompatibilityTest(SimpleTestCase):
    def test_score_food_preferences(self, **overrides):
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
        first = self.test_score_food_preferences()
        second = self.test_score_food_preferences()
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

    def test_price_and_atmosphere_match(self):
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
            favorite_cuisine = "",
            favorite_food = "",
            preferred_price_range = "",
            preferred_dining_atmosphere = "",
            willing_to_try_new_foods = None,
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
