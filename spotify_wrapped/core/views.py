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
import uuid
from django.core.mail import send_mail
from django.conf import settings
from .models import Invite
from .models import SpotifyWrap
from django.contrib.auth import login


def index(request):
    """
    Renders the homepage of the application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered homepage template.
    """
    return render(request, 'core/index.html')

def register(request):
    """
    Handles user registration.

    If the request method is POST, it processes the registration form and
    creates a new user if the form is valid. Otherwise, it renders the
    registration form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered registration template or a redirect to the login page after successful registration.
    """
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
@csrf_exempt
def describe_music_taste(request):
    """
    Generates a dynamic description of the user's music taste.

    If a POST request is made:
        - Retrieves user input for music data or fetches the top artist from Spotify data.
        - Uses the Groq API to generate a description based on the user's music data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the generated description or an error message.
        HttpResponse: The rendered template if the request method is not POST.
    """
    if request.method == "POST":
        user_music_data = request.POST.get("music_data")
        user = request.user

        # If user_music_data is empty, fetch dynamic Spotify data
        if not user_music_data:
            try:
                # Fetch the latest SpotifyWrap and use the top artist
                spotify_wrap = SpotifyWrap.objects.filter(user=user).latest('created_at')
                top_artists = spotify_wrap.data.get('top_artists', [])
                if top_artists:
                    user_music_data = top_artists[0]  # Use the top artist
                else:
                    return JsonResponse({"error": "No top artists data found. Please input your music taste manually."}, status=400)
            except SpotifyWrap.DoesNotExist:
                return JsonResponse({"error": "No Spotify data found. Please input your music taste manually."}, status=400)

        client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        # Use the top artist in the prompt
        question = f"Describe how someone who listens to {user_music_data} tends to act, think, and dress. Keep it short and sweet."

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
#REDIRECT_URI = 'http://localhost:8000/callback/'  # Make sure this matches what you set in the Spotify dashboard

#REDIRECT_URI = "http://128.61.9.117:8000/callback/"

SCOPE = 'user-top-read user-read-recently-played'  # Permissions you're asking for

from urllib.parse import urlencode

def spotify_auth_url(request):
    """
    Constructs the Spotify authorization URL with required parameters.

    This function generates the URL for Spotify's authorization endpoint,
    including the client ID, response type, redirect URI, and requested scopes.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The full Spotify authorization URL with query parameters.
    """
    redirect_uri = get_redirect_uri(request)
    print(f"Using redirect URI: {redirect_uri}")  # Log the redirect URI for debugging
    auth_base_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPE,
    }
    return f"{auth_base_url}?{urlencode(params)}"




def spotify_login(request):
    """
    Redirects the user to Spotify's login page.

    This function uses the `spotify_auth_url` function to generate the Spotify
    authorization URL and redirects the user to it.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect to Spotify's authorization page.
    """
    return redirect(spotify_auth_url(request))


def get_redirect_uri(request):
    """
    Dynamically generates the redirect URI for the Spotify authorization flow.

    This function constructs the redirect URI based on the current request's host,
    ensuring compatibility with the application's deployment environment.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The dynamically generated redirect URI.
    """
    host = request.get_host()  # Get the host, e.g., '128.61.9.117:8000'
    return f"http://{host}/callback/"




from django.http import JsonResponse

from django.contrib.auth.models import User


from django.contrib.auth import login

from django.contrib.auth import login
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

def spotify_callback(request):
    """
    Handles the Spotify authorization callback to exchange the authorization code for an access token.

    This function:
    1. Retrieves the authorization code from the callback request.
    2. Exchanges the authorization code for an access token using Spotify's API.
    3. Fetches the user's Spotify profile information.
    4. Creates or retrieves a Django user based on the Spotify ID.
    5. Logs the user into the application and stores the access token in the session.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the homepage if successful or renders an error page if any step fails.
    """
    code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': get_redirect_uri(request),
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return render(request, 'core/error.html', {'error': 'Failed to obtain access token from Spotify'})

    token_info = response.json()
    access_token = token_info.get('access_token')

    if not access_token:
        return render(request, 'core/error.html', {'error': 'Access token not found in Spotify response'})

    # Fetch Spotify user profile
    user_profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_profile_url, headers=headers)

    if user_response.status_code != 200:
        return render(request, 'core/error.html', {'error': 'Failed to fetch user profile from Spotify'})

    user_data = user_response.json()
    spotify_id = user_data.get('id')  # Unique Spotify ID
    email = user_data.get('email', f"{spotify_id}@example.com")  # Fallback email
    display_name = user_data.get('display_name', f"Spotify User {spotify_id[:8]}")  # Fallback display name

    # Create or get the Django user
    user, created = User.objects.get_or_create(
        username=spotify_id,
        defaults={'email': email, 'first_name': display_name}
    )

    # Log the user in
    login(request, user)

    # Store the access token in the session
    request.session['spotify_token'] = access_token
    request.session['display_name'] = display_name

    return redirect('index')



import requests

def get_user_top_tracks(token):
    """
    Retrieves the user's top tracks from Spotify.

    This function sends a GET request to Spotify's API to fetch the user's most played tracks.
    The authorization token is required to authenticate the request.

    Args:
        token (str): The Spotify access token for the user.

    Returns:
        dict or None: A dictionary containing the user's top tracks if the request is successful,
                      otherwise None if the request fails.
    """
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

def get_user_top_artists(token, time_range="long_term", limit=10):
    """
    Retrieves the user's top artists from Spotify within a specified time range.

    Args:
        token (str): The Spotify access token for the user.
        time_range (str): The time range for top artists (e.g., "short_term", "medium_term", "long_term").
        limit (int): The maximum number of top artists to fetch (default is 10).

    Returns:
        dict or None: A dictionary containing the user's top artists if the request is successful,
                      otherwise None if the request fails.
    """
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "limit": limit,  # Limit the number of artists to fetch
        "time_range": time_range  # Use the time_range parameter
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
    """
    Retrieves the user's top tracks from Spotify within a specified time range.

    Args:
        token (str): The Spotify access token for the user.
        time_range (str): The time range for top tracks (e.g., "short_term", "medium_term", "long_term").
        limit (int): The maximum number of top tracks to fetch (default is 8).

    Returns:
        dict or None: A dictionary containing the user's top tracks if the request is successful,
                      otherwise None if the request fails.
    """
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

def get_recently_played(token, limit=50):
    """
    Retrieves the user's recently played tracks from Spotify.

    Args:
        token (str): The Spotify access token for the user.
        limit (int): The maximum number of recently played tracks to fetch (default is 50).

    Returns:
        dict or None: A dictionary containing the user's recently played tracks if the request is successful,
                      otherwise None if the request fails.
    """
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

# Updated show_summary view
from .models import SpotifyWrap
from django.contrib.auth.decorators import login_required

@login_required
def show_summary(request):
    """
    Handles the Spotify wrap summary generation for a selected time range (short, medium, or long term).

    This function retrieves the user's Spotify top tracks, top artists, and recently played tracks based on
    the selected term (time range). It calculates additional insights like total minutes listened and most
    played genres. The data is saved in the database and rendered on the summary page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the summary page with the wrap data if successful.
        HttpResponseRedirect: Redirects to the login page if no token is available.
        HttpResponseRedirect: Redirects to the homepage if the request is not a POST request.
    """
    token = request.session.get('spotify_token')
    if request.method == "POST":
        term = request.POST.get('term', 'long_term')  # Default to "long_term" if no term is provided

        if token:
            # Retrieve data for the selected term
            top_tracks = get_user_top_tracks(token, time_range=term)
            top_artists = get_user_top_artists(token, time_range=term)
            recently_played = get_recently_played(token)

            # Get the most played song for the selected term
            most_played_track = (
                top_tracks['items'][0] if top_tracks and 'items' in top_tracks and top_tracks['items'] else None
            )

            # Calculate total minutes listened from recently played tracks
            total_minutes = 0
            if recently_played:
                total_duration_ms = sum(item['track']['duration_ms'] for item in recently_played.get('items', []))
                total_minutes = total_duration_ms / 60000  # Convert milliseconds to minutes

            # Check if data is present
            if top_tracks and top_artists and recently_played and most_played_track:
                genres = [artist.get('genres', []) for artist in top_artists.get('items', [])]
                unique_genres = list(set(genre for sublist in genres for genre in sublist))

                # Limit to 8 genres
                limited_genres = unique_genres[:8]

                # Create the wrap data dictionary
                wrap_data = {
                    'top_tracks': top_tracks.get('items', []),
                    'top_artists': top_artists.get('items', []),
                    'genres': limited_genres,
                    'recently_played': recently_played.get('items', []),
                    'most_played_track': most_played_track,
                    'total_minutes': total_minutes,
                    'term': term.replace('_term', '').capitalize(),  # Pass the selected term for the template
                }

                # Save wrap to the database
                SpotifyWrap.objects.create(
                    user=request.user,
                    title=f"My Spotify Wrap ({term.replace('_term', '').capitalize()})",
                    term=term.replace('_term', ''),  # Save as 'short', 'medium', or 'long'
                    data=wrap_data
                )

                # Render the summary template with the wrap data
                return render(request, 'core/summary.html', wrap_data)

            else:
                # Render an error page if some data is missing
                return render(request, 'core/error.html', {
                    'error': "Failed to retrieve all Spotify data for the selected term. Please try again later."
                })
        else:
            # Redirect to login if no token is available
            return redirect('spotify_login')

    # If not a POST request, redirect to the homepage
    return redirect('index')



from django.shortcuts import render

def play_top_tracks(request):
    """
    Fetches and plays the user's top 5 tracks from Spotify.

    This function retrieves the user's top tracks from Spotify and passes them to the
    template for playback. If the data cannot be retrieved, an error page is displayed.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the play_top_tracks.html template with the top tracks.
        HttpResponseRedirect: Redirects to the Spotify authorization URL if no token is available.
    """
    token = request.session.get('spotify_token')

    if token:
        # Retrieve top tracks with a limit of 5
        top_tracks = get_user_top_tracks(token)

        if top_tracks:
            # Include 'preview_url' in the context
            return render(request, 'core/play_top_tracks.html', {
                'top_tracks': top_tracks.get('items', [])[:5]
            })
        else:
            return render(request, 'core/error.html', {
                'error': "Failed to retrieve top tracks."
            })
    else:
        return redirect(spotify_auth_url())


from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from core.forms import ContactForm

def contact_developers(request):
    """
    Handles user feedback submission and sends an email to the development team.

    This function displays a contact form where users can provide their name, email,
    and message. If the form is valid, the message is sent to the developers, and the
    user is redirected to a thank-you page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the contact_developers.html template with the form.
        HttpResponseRedirect: Redirects to a thank-you page after the form is submitted successfully.
    """
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
    """
    Renders a thank-you page after the user has completed a specific action,
    such as sending feedback or an invitation.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the thank_you.html template.
    """
    return render(request, 'core/thank_you.html')

def generate_invite_code():
    """
    Generates a unique invite code using UUID.

    This function creates a universally unique identifier (UUID) that can be used
    as an invitation code to uniquely identify each invitation.

    Returns:
        str: A string representation of the generated UUID.
    """
    return str(uuid.uuid4())

def invite_friend(request):
    """
    Allows a user to invite a friend via email to join the platform.

    This function handles the POST request to create an invitation. It generates a unique
    invite code, saves the invitation to the database, and sends an email to the recipient
    with a registration link containing the invite code.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the invite_friend.html template for GET requests.
        HttpResponseRedirect: Redirects to the 'invite_sent' page after successfully
                              sending an invitation email.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        invite_code = generate_invite_code()
        invite = Invite.objects.create(sender=request.user, recipient_email = email, invite_code=invite_code)

        send_mail(
            'Your Invitation to Join!',
            f"You've been invited! Use this link to sign up: {settings.SITE_URL}/register?invite_code={invite_code}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        return redirect('invite_sent')
    return render(request, 'core/invite_friend.html')


from django.contrib.auth.decorators import login_required

@login_required
def list_wraps(request):
    """
    Fetches and displays a list of all SpotifyWrap entries for the current user.

    This function retrieves all SpotifyWrap objects associated with the logged-in user,
    ordered by creation date in descending order, and renders them on the `list_wraps.html` template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the `list_wraps.html` template with the list of wraps.
    """
    wraps = SpotifyWrap.objects.filter(user=request.user).order_by('-created_at')  # Fetch wraps for the current user
    return render(request, 'core/list_wraps.html', {'wraps': wraps})

from django.shortcuts import get_object_or_404

@login_required
def view_wrap(request, wrap_id):
    """
    Fetches and displays details of a specific SpotifyWrap entry for the current user.

    This function retrieves a specific SpotifyWrap object by its ID, ensuring that the
    wrap belongs to the logged-in user. The details are rendered on the `view_wrap.html` template.

    Args:
        request (HttpRequest): The HTTP request object.
        wrap_id (int): The ID of the SpotifyWrap object to be retrieved.

    Returns:
        HttpResponse: Renders the `view_wrap.html` template with the wrap details.
        Http404: If the SpotifyWrap object is not found or does not belong to the user.
    """
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)  # Ensure the wrap belongs to the user
    return render(request, 'core/view_wrap.html', {'wrap': wrap})


from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def delete_wrap(request, wrap_id):
    """
    Deletes a specific SpotifyWrap entry for the current user.

    This function ensures that the SpotifyWrap object to be deleted belongs to the logged-in user.
    If the request method is POST, the wrap is deleted, and the user is redirected to the list of wraps.

    Args:
        request (HttpRequest): The HTTP request object.
        wrap_id (int): The ID of the SpotifyWrap object to be deleted.

    Returns:
        HttpResponseRedirect: Redirects to the `list_wraps` page after successful deletion.
        Http404: If the SpotifyWrap object is not found or does not belong to the user.
    """
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)  # Ensure the wrap belongs to the user
    if request.method == 'POST':
        wrap.delete()
    return HttpResponseRedirect(reverse('list_wraps'))

def delete_account(request):
    """
    Deletes the current user's account and all associated data.

    This function handles the deletion of the logged-in user's account, including
    all associated SpotifyWrap entries. After deletion, the user is redirected to
    the homepage.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the `delete_account.html` template for confirmation.
        HttpResponseRedirect: Redirects to the homepage (`index`) after account deletion.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()  # Deletes the user and all associated data (including SpotifyWraps)
        return redirect('index')  # Redirect to the homepage after deletion
    return render(request, 'core/delete_account.html')