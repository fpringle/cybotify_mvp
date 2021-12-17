from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from api.music.models import UserPlaylist
from api.stats.views import get_playlist_average_features


def index(request):
    return render(request, "index.html")


def needs_spotify_user(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "spotifyuser"):
            return render(request, "register.html")
        return func(request, *args, **kwargs)

    return wrapper


# music
@login_required
@needs_spotify_user
def playlists(request):
    context = {
        "url": reverse("playlists"),
        "detail_url": reverse("frontend:playlist-detail", args=(1,)),
    }
    return render(request, "playlists.html", context)


# stats
@login_required
def playlist_detail(request, playlist_id):
    if not UserPlaylist.objects.filter(pk=playlist_id).exists():
        raise Http404("The playlist you're trying to look at doesn't exist")

    playlist = UserPlaylist.objects.get(pk=playlist_id)
    if not playlist.is_user_allowed(request.user):
        raise PermissionDenied("You don't have permission to view that playlist.")

    if playlist.needs_update()[0]:
        print("playlist is out of date, updating")
        context = {
            "ws_url": f"/ws/playlist_detail/{playlist_id}/",
        }

        return render(request, "playlist_detail_ws.html", context)

    else:
        print("no need to update")
        context = {
            "playlist": playlist,
            "features": get_playlist_average_features(playlist),
        }
        return render(request, "playlist_detail.html", context)


# accounts
@login_required
def profile(request):
    return render(request, "profile.html")


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")
    return render(request, "register.html")


def create_password(request):
    return render(request, "create_password.html")
