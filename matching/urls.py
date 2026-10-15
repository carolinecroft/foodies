from django.urls import path
from . import views

urlpatterns = [
    path('discover/', views.discovery, name='discovery'),
    path('matches/', views.matches, name='matches'),
    path('compatibility/', views.compatibility, name='compatibility'),
]