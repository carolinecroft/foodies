from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Bio and profile prompt are optional; other profile inputs are required
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(validators=[MinValueValidator(18)])
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    interested_in = models.JSONField(default=list)
    distance_preference = models.PositiveIntegerField(
        default=25,
        validators=[MinValueValidator(1)],
    )
    profile_prompt = models.CharField(max_length=300, blank=True)
    

    def __str__(self):
        return self.name

class FoodPreferences(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    
    favorite_cuisine = models.CharField(max_length=100)
    disliked_cuisine = models.CharField(max_length=100, blank=True)
    dietary_restrictions = models.CharField(max_length=100, blank=True)
    favorite_food = models.CharField(max_length=100, blank=True)
    preferred_price_range = models.CharField(max_length=20)
    preferred_dining_atmosphere = models.CharField(max_length=100)
    willing_to_try_new_foods = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profile.name}'s Food Preferences"