from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Interaction, Match

@transaction.atomic
def record_interaction(actor, target, action):
    # Make sure the action is valid
    if action not in [Interaction.LIKE, Interaction.PASS]:
        raise ValidationError("Action must be 'like' or 'pass'.")

    # Users cannot like or pass themselves
    if actor.pk == target.pk:
        raise ValidationError("You cannot interact with yourself.")

    # Prevent duplicate interactions
    if Interaction.objects.filter(actor=actor, target=target).exists():
        raise ValidationError("You have already interacted with this user.")

    # Save the interaction
    interaction = Interaction.objects.create(
        actor=actor,
        target=target,
        action=action,
    )

    # Only likes can create matches
    if action == Interaction.LIKE:
        # Check whether the other user already liked this user
        reciprocal_like = Interaction.objects.filter(
            actor=target,
            target=actor,
            action=Interaction.LIKE,
        ).exists()

        if reciprocal_like:
            # Always store the smaller user ID first
            user1, user2 = sorted(
                [actor, target],
                key=lambda user: user.pk,
            )

            # Create a match only if one does not already exist
            Match.objects.get_or_create(
                user1=user1,
                user2=user2,
            )

    return interaction
