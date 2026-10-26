from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Interaction, Match
from .services import record_interaction


User = get_user_model()


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
