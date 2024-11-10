from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth.views import LoginView  # Import LoginView
from . import views  # This imports views from the same core directory



urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('login/', views.login, name='login'),  # Spotify OAuth login route
    path('register/', views.register, name='register'),  # Custom registration (if needed)
    path('callback/', views.spotify_callback, name='callback'),  # Spotify OAuth callback
    path('summary/', views.show_summary, name='show_summary'),  # Show user's top tracks
    path('describe-music/', views.describe_music_taste, name='describe_music_taste'),
    path('contact/', views.contact_developers, name='contact_developers'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('play-top-tracks/', views.play_top_tracks, name='play_top_tracks'),
]
