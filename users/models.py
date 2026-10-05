from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower 

from .manager import UserManager
# Create your models here.

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='unique_email_case_insensitive_unique'
            )
        ]

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def save(self, *args, **kwargs):
        self.email = type(self).objects.normalize_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email