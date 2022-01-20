import datetime
import logging

from django.contrib.auth import login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import is_password_usable, make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import SpotifyManager
from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials, User
from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None, format=None):
        if pk is None:
            user = request.user
        else:
            if not (pk == request.user.pk or request.user.is_superuser):
                return Response(status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(pk=pk)

        serializer = UserSerializer(user)
        return Response(serializer.data)


@api_view(["GET"])
def new_user(request):
    logger.info("Request for new user")
    reg = RegistrationState.objects.create_state()
    if request.user.is_authenticated:
        reg.user = request.user
    reg.save()
    logger.info("Generated state string: %s", reg.state_string)
    url = SpotifyManager.authorize_url(reg.state_string)
    logger.info("Redirecting user to: %s", url)
    return HttpResponseRedirect(url)


@api_view(["GET"])
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
    logger.info("Spotify ID: %s", spotify_id)

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
        return HttpResponseRedirect(reverse("frontend:create-password"))
    return HttpResponseRedirect(reverse("frontend:index"))


@api_view(["GET"])
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse("frontend:index"))


@api_view(["POST"])
def create_password(request):
    user_id = request.user.pk
    user = User.objects.filter(pk=user_id).get()

    username = request.POST.get("username")
    password = request.POST.get("password")

    user.username = username
    user.password = make_password(password)
    user.save()
    login(request, user)
    return HttpResponseRedirect(reverse("frontend:index"))
