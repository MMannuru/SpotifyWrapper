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


from django.http import JsonResponse

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
    
    # Print the response for debugging if there’s an error
    if response.status_code != 200:
        print("Spotify API error:", response.status_code, response.text)
        return JsonResponse({'error': 'Failed to obtain access token from Spotify'}, status=500)
    
    token_info = response.json()
    
    # Ensure access token is in the response
    access_token = token_info.get('access_token')
    if not access_token:
        print("Error: Access token not found in response.")
        return JsonResponse({'error': 'Access token not found in Spotify response'}, status=500)

    # Store the access token in the session
    request.session['spotify_token'] = access_token

    # Redirect to the summary page or any other page where you will show the user's Spotify data
    return redirect('show_summary')




def get_user_top_tracks(token):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Check if 'items' list is empty
        if not data.get('items'):
            print("No top tracks found for this user.")
            return {"items": []}  # Return an empty list if no top tracks are available
        return data
    else:
        # Log the error if Spotify returns an error code
        print(f"Spotify API error: {response.status_code} - {response.text}")
        return {"error": f"Spotify API returned status code {response.status_code}"}




def show_summary(request):
    # Get the access token from session
    token = request.session.get('spotify_token')

    if token:
        # Fetch user's top tracks
        top_tracks = get_user_top_tracks(token)
        
        # Check if there was an error in the response
        if "error" in top_tracks:
            # Clear the session token and redirect to login to refresh it
            del request.session['spotify_token']  # Remove invalid token
            return redirect('login')

        # Check if there are any top tracks
        if not top_tracks.get('items'):
            return render(request, 'core/summary.html', {
                'message': 'No listening history found for this user.',
            })

        # Render the summary page and pass the top tracks data to the template
        return render(request, 'core/summary.html', {
            'top_tracks': top_tracks['items'],
        })
    else:
        # If no token is found, redirect to login
        return redirect('login')





