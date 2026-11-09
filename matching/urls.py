from django.urls import path
from . import views

urlpatterns = [
    path('discover/', views.discovery, name='discovery'),
    path('interact/<int:profile_id>/', views.interact, name='interact'),
    path('matches/', views.matches, name='matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('compatibility/', views.compatibility, name='compatibility'),
    path('compatibility/<int:profile_id>/', views.compatibility, name='compatibility_detail'),
]
