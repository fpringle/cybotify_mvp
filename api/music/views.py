from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from api.accounts.views import needs_spotify_user


@login_required
@needs_spotify_user
def playlists(request):
    su = request.user.spotifyuser
    su.update_playlists()
    playlists = su.userplaylist_set.all().order_by("name")
    playlist_data = [
        {
            #            "id": pl.pk,
            #            "spotify_id": pl.spotify_id,
            "name": pl.name,
            "last_updated": pl.last_updated,
            "status": pl.status,
            "url": reverse("playlist-detail", args=(pl.pk,)),
        }
        for pl in playlists
    ]
    context = {"playlists": playlists, "playlist_data": playlist_data}
    return render(request, "playlists.html", context)
