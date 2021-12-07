from functools import wraps
import datetime
import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import is_password_usable
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials, User
from .spotify_client_info import get_spotify_oauth, get_spotify_user_client, scopes


logger = logging.getLogger(__name__)

def new_user(request):
    logger.info("Request for new user")
    reg = RegistrationState()
    if request.user.is_authenticated:
        reg.user = request.user
    reg.save()
    logger.info("Generated state string: %s", reg.state_string)
    oauth = get_spotify_oauth(scopes)
    url = oauth.get_authorize_url(state=reg.state_string)
    logger.info("Redirecting user to: %s", url)
    return HttpResponseRedirect(url)


def handle_spotify_auth_response(request):
    logger.info("Response from spotify auth")
    code = request.GET.get("code")
    state = request.GET.get("state")

    if (not code) or (not state):
        # handle error
        pass

    logger.info("Auth code: %s", code)
    logger.info("State string: %s", state)

    query = RegistrationState.objects.filter(state_string = state)
    length = query.count()
    if length == 0:
        # handle bad state string
        pass
    elif length > 1:
        # handle duplicate state string
        pass

    reg = query.get()

    oauth = get_spotify_oauth(scopes)

    logger.info("Getting access token from Spotify API")

    token_info = oauth.get_access_token(code)

    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]
    expires_at = datetime.datetime.fromtimestamp(
        token_info["expires_at"], datetime.timezone.utc
    )

    logger.info("Access token: %s", access_token)
    logger.info("Refresh token: %s", refresh_token)
    logger.info("Expires at: %s", expires_at)

    sp = get_spotify_user_client(access_token)
    user_info = sp.current_user()

    spotify_id = user_info["id"]
    print("spotify id:", spotify_id)

    if SpotifyUser.objects.filter(spotify_id=spotify_id).exists():
        # user already exists
        reg.delete()
        return HttpResponse("User already exists!")

    email = user_info.get("email", "")
    name = user_info.get("display_name", "")
    first_name, *rest = name.strip().split()
    last_name = " ".join(rest)

    logger.info("User name: %s %s", first_name, last_name)
    logger.info("User email: %s", email)
    logger.info("User Spotify ID: %s", spotify_id)

    if reg.user:
        user = reg.user
    else:
        print("create new user")
        user = User.objects.create_user(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

    su = SpotifyUser(user=user, spotify_id=spotify_id)
    su.save()

    cred = SpotifyUserCredentials.objects.create(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )
    cred.save()

    reg.delete()

    login(request, user)
    if not (hasattr(user, "password") and is_password_usable(user.password)):
        return HttpResponseRedirect('/user/new/create_password/')
    return HttpResponseRedirect('/')

def user_index(request):
    return render(request, 'index_loggedin.html')

def anon_index(request):
    return render(request, 'index_anon.html')

def index(request):
    if request.user.is_authenticated:
        return user_index(request)
    else:
        return anon_index(request)

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')

def create_password(request):
    if request.method == "GET":
        return render(request, "create_password.html")
    print("post create pass")
    user_id = request.user.pk
    user = User.objects.filter(pk=user_id).get()

    username = request.POST.get("username")
    password = request.POST.get("password")

    user.username = username
    user.password = make_password(password)
    user.save()
    login(request, user)
    return HttpResponseRedirect('/')

def needs_spotify_user(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "spotifyuser"):
            return render(request, "register.html")
        return func(request, *args, **kwargs)
    return wrapper

@login_required
@needs_spotify_user
def playlists(request):
    su = request.user.spotifyuser
    su.update_playlists()
    playlists = su.userplaylist_set.all().order_by('name')
    context = {
        "playlists": playlists,
    }
    return render(request, 'playlists.html', context)

@login_required
def profile(request):
    return render(request, 'profile.html')

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request, 'register.html')