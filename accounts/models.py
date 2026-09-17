from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # we don't want these fields to be optional (except for bio) when creating a profile, so we will not set blank=True or null=True for these fields
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    

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