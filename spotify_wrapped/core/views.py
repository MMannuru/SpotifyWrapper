from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
import requests
from groq import Groq
import requests
import urllib.parse
from django.contrib.auth.decorators import login_required


# Index view
def index(request):
    return render(request, 'core/index.html')


# Register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = UserCreationForm()

    return render(request, 'core/register.html', {'form': form})

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from groq import Groq

@csrf_exempt
def describe_music_taste(request):
    if request.method == "POST":
        user_music_data = request.POST.get("music_data")

        client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        question = f"Describe how someone who listens to {user_music_data} tends to act, think, and dress."

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                model="llama3-8b-8192",
            )
            answer_text = chat_completion.choices[0].message.content
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse({"description": answer_text})

    return render(request, "core/describe_music.html")

# Your Spotify app credentials
CLIENT_ID = '85fd30dd498c4fbeac1e658423614b52'
CLIENT_SECRET = '0626ce38d1ad488fa8ae081f31d07b07'
REDIRECT_URI = 'http://localhost:8000/callback/'  # Make sure this matches what you set in the Spotify dashboard
SCOPE = 'user-top-read user-read-recently-played'  # Permissions you're asking for


# Function to create Spotify Auth URL
def spotify_auth_url():
    auth_base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    url = f"{auth_base_url}?{urllib.parse.urlencode(params)}"
    return url


# Login view that redirects to Spotify's authorization page
def login(request):
    return redirect(spotify_auth_url())


# Handle the callback from Spotify and exchange the authorization code for an access token
def spotify_callback(request):
    code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    token_info = response.json()

    # Extract the access token and store it in the session
    access_token = token_info['access_token']
    request.session['spotify_token'] = access_token

    # Redirect to the summary page or any other page where you will show the user's Spotify data
    return redirect('index')


import requests

def get_user_top_tracks(token):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve top tracks:", response.status_code, response.text)
        return None

import requests
import json

def get_user_top_artists(token):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "limit": 10  # Limit to 10 artists for testing
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        top_artists = response.json()

        # Debug: Print the entire response to verify data structure
        print("Top artists response:", json.dumps(top_artists, indent=2))

        # Check if genres exist in the response
        for artist in top_artists.get("items", []):
            if "genres" in artist:
                print(f"Artist: {artist['name']}, Genres: {artist['genres']}")
            else:
                print(f"Artist: {artist['name']} has no genres listed.")

        return top_artists
    else:
        print("Failed to retrieve top artists:", response.status_code, response.text)
        return None

def get_user_top_tracks(token, time_range="long_term", limit=8):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "time_range": time_range,
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve top tracks:", response.status_code, response.text)
        return None



def get_recently_played(token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve recently played tracks:", response.status_code, response.text)
        return None

def get_recently_played(token, limit=50):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "limit": limit
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve recently played tracks:", response.status_code, response.text)
        return None

import json

# Show summary view to display top tracks
def show_summary(request):
    token = request.session.get('spotify_token')
    if token:
        # Retrieve data
        top_tracks = get_user_top_tracks(token)
        top_artists = get_user_top_artists(token)
        recently_played = get_recently_played(token)

        # Get the most played song (top track from long-term)
        most_played_track_data = get_user_top_tracks(token, time_range="long_term")
        most_played_track = most_played_track_data['items'][0] if most_played_track_data and 'items' in most_played_track_data else None

        # Calculate total minutes listened
        total_minutes = 0
        if recently_played:
            total_duration_ms = sum(item['track']['duration_ms'] for item in recently_played.get('items', []))
            total_minutes = total_duration_ms / 60000  # Convert milliseconds to minutes

        # Debugging output
        print(f"Total Minutes Listened: {total_minutes:.2f}")

        # Check if data is present
        if top_tracks and top_artists and recently_played and most_played_track:
            genres = [artist.get('genres', []) for artist in top_artists.get('items', [])]
            unique_genres = set(genre for sublist in genres for genre in sublist)

            return render(request, 'core/summary.html', {
                'top_tracks': top_tracks.get('items', []),
                'top_artists': top_artists.get('items', []),
                'genres': unique_genres,
                'recently_played': recently_played.get('items', []),
                'most_played_track': most_played_track,
                'total_minutes': total_minutes  # Pass total minutes to template
            })
        else:
            return render(request, 'core/error.html', {
                'error': "Failed to retrieve all Spotify data. Please try again later."
            })
    else:
        return redirect('login')

from django.shortcuts import render

def play_top_tracks(request):
    token = request.session.get('spotify_token')

    if token:
        # Retrieve top tracks with a limit of 5
        top_tracks = get_user_top_tracks(token, limit=5)

        if top_tracks:
            return render(request, 'core/play_top_tracks.html', {
                'top_tracks': top_tracks.get('items', [])
            })
        else:
            # Redirect to Spotify authorization page if user isn't logged in
            return redirect(spotify_auth_url())


# views.py
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from core.forms import ContactForm


def contact_developers(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Send email to developers
            email_message = EmailMessage(
                f"Feedback from {name}",
                message,
                email,
                ['dummyemail@gmail.com']
            )
            email_message.send()
            return redirect('thank_you')  # Redirect to a thank you page after submission
    else:
        form = ContactForm()
    return render(request, 'core/contact_developers.html', {'form': form})

# core/views.py

from django.shortcuts import render

def thank_you(request):
    return render(request, 'core/thank_you.html')
