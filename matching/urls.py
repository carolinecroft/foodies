from django.urls import path
from . import views

urlpatterns = [
    path('discover/', views.discovery, name='discovery'),
    path('matches/', views.matches, name='matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    path('compatibility/', views.compatibility, name='compatibility'),
]
