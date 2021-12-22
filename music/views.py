from accounts.views import needs_spotify_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from music.models import SpotifyUserPlaylistRelationship


@login_required
@needs_spotify_user
def playlists(request):
    su = request.user.spotifyuser
    su.update_playlists()
    playlists = [
        x.playlist
        for x in SpotifyUserPlaylistRelationship.objects.filter(user=su).order_by(
            "playlist_position"
        )
    ]
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