import datetime
import logging
from functools import wraps

from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import is_password_usable, make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from . import SpotifyManager
from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials, User

logger = logging.getLogger(__name__)


def new_user(request):
    logger.info("Request for new user")
    reg = RegistrationState()
    if request.user.is_authenticated:
        reg.user = request.user
    reg.save()
    logger.info("Generated state string: %s", reg.state_string)
    url = SpotifyManager.authorize_url(reg.state_string)
    logger.info("Redirecting user to: %s", url)
    return HttpResponseRedirect(url)


def handle_spotify_auth_response(request):
    logger.info("Response from spotify auth")
    code = request.GET.get("code")
    state = request.GET.get("state")

    if (not code) or (not state):
        logger.error("received bad forwarded request from Spotify")
        logger.error("error: request missing user code or state string")
        logger.error("path:", request.path)
        logger.error("params:", request.GET)
        return HttpResponse("Bad response from Spotify", status=502)

    logger.info("Auth code: %s", code)
    logger.info("State string: %s", state)

    query = RegistrationState.objects.filter(state_string=state)
    if not query.exists():
        logger.error("received bad forwarded request from Spotify")
        logger.error("error: state string did not match any string in the DB")
        logger.error("path:", request.path)
        logger.error("params:", request.GET)
        return HttpResponse("Bad response from Spotify", status=502)

    reg = query.get()

    logger.info("Getting access token from Spotify API")

    token_info = SpotifyManager.get_tokens(code)

    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]
    expires_at = datetime.datetime.fromtimestamp(
        token_info["expires_at"], datetime.timezone.utc
    )

    logger.info("Access token: %s", access_token)
    logger.info("Refresh token: %s", refresh_token)
    logger.info("Expires at: %s", expires_at)

    user_info = SpotifyManager.user_client(access_token).current_user()

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
        user = User.objects.create_user(username=spotify_id, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

    su = SpotifyUser(user=user, spotify_id=spotify_id)
    su.save()

    cred = SpotifyUserCredentials.objects.create(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    cred.save()

    reg.delete()

    login(request, user)
    if not (hasattr(user, "password") and is_password_usable(user.password)):
        return HttpResponseRedirect("/accounts/new/create_password/")
    return HttpResponseRedirect("/")


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect("/")


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
    return HttpResponseRedirect("/")


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
    playlists = su.userplaylist_set.all().order_by("name")
    context = {
        "playlists": playlists,
    }
    return render(request, "playlists.html", context)


@login_required
def profile(request):
    return render(request, "profile.html")


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    return render(request, "register.html")
