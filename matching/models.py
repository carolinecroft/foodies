from django.conf import settings
from django.db import models

class Interaction(models.Model):
    LIKE = "like"
    PASS = "pass"

    CHOICES = [
        (LIKE, "Like"),
        (PASS, "Pass"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interactions_sent",
    )

    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interactions_received",
    )

    action = models.CharField(
        max_length=4,
        choices=CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["actor", "target"],
                name="unique_user_interaction",
            ),
            models.CheckConstraint(
                condition=~models.Q(actor=models.F("target")),
                name="prevent_self_interaction",
            ),
        ]

    def __str__(self):
        return f"{self.actor} {self.action} {self.target}"


class Match(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user1",
    )

    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user2",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_match_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(user1_id__lt=models.F("user2_id")),
                name="ordered_match_pair",
            ),
        ]

    def __str__(self):
        return f"Match between {self.user1} and {self.user2}"
