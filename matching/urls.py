from django.urls import path
from . import views

urlpatterns = [
    path('discover/', views.discovery, name='discover'),
    path('interact/<int:profile_id>/', views.interact, name='interact'),
    path('matches/', views.matches, name='matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path("liked-you/", views.compatibility, name="Liked_You"),
]
