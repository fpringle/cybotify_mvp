from functools import wraps

from django.contrib.auth import logout as auth_logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden

from .models import User, SpotifyUser, UserPlaylist, Track, TrackFeatures

from server.stats.views import get_playlist_average_features

def user_index(request):
    return render(request, 'frontend/index_loggedin.html')

def anon_index(request):
    return render(request, 'frontend/index_anon.html')

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
        return render(request, "frontend/create_password.html")
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
            return render(request, "frontend/register.html")
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
    return render(request, 'frontend/playlists.html', context)

@login_required
def playlist_detail(request, playlist_id):
    playlist = UserPlaylist.objects.filter(pk=playlist_id).get()
    if request.user != playlist.user.user:
        return HttpResponseForbidden("That's not your playlist!")

    playlist.check_update()
    context = {
        "playlist": playlist,
        "features": get_playlist_average_features(playlist),
    }

    return render(request, 'frontend/playlist_detail.html', context)

@login_required
def profile(request):
    return render(request, 'frontend/profile.html')

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request, 'frontend/register.html')
