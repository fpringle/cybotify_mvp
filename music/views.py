from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.views import needs_spotify_user

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
