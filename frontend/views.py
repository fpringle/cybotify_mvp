from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from api.music.models import UserPlaylist


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

    context = {
        "playlist_url": reverse("playlist-detail", args=(playlist_id,)),
        "analysis_url": reverse("playlist-analysis", args=(playlist_id,)),
    }
    return render(request, "playlist_detail.html", context)


# accounts
@login_required
def profile(request):
    return render(request, "profile.html")


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("frontend:index"))
    return render(request, "register.html")


def create_password(request):
    return render(request, "create_password.html")
