import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from music.models import UserPlaylist

from .spotify_client_info import (
    get_all_playlists,
    get_playlist_status,
    get_spotify_oauth,
    get_spotify_user_client,
    scopes,
)
from .util import random_string


class RegistrationState(models.Model):
    state_string = models.CharField(max_length=16)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.state_string = self.__class__.unique_random_string(16)
        self.state_string = random_string(16)

    @classmethod
    def unique_random_string(cls, length):
        string = random_string(16)
        while cls.objects.filter(state_string=string).exists():
            string = random_string(16)
        return string

    class Meta:
        verbose_name = "User pending registration"
        verbose_name_plural = "Users pending registration"


class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    spotify_id = models.CharField(max_length=256)

    def __str__(self):
        return f"(email={self.user.email}, spotifyID={self.spotify_id})"

    def new_playlist(self, playlist_data):
        # print(playlist_data)
        playlist = UserPlaylist.objects.create(
            spotify_id=playlist_data["id"],
            name=playlist_data["name"],
            # snapshot_id=playlist_data["snapshot_id"],
            user=self,
            status=get_playlist_status(playlist_data),
        )
        playlist.save()
        # playlist.update_tracks()

    def update_playlists(self):
        self.user.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(self.user.spotifyusercredentials.access_token)
        playlists = get_all_playlists(sp)
        # TODO: drop playlists that are no longer present
        for playlist in playlists:
            spotify_id = playlist["id"]
            # TODO: move this to UserPlaylist?
            if UserPlaylist.objects.filter(spotify_id=spotify_id).exists():
                pl = UserPlaylist.objects.get(spotify_id=spotify_id)
                print("playlist", pl.name, "already exists")
                print(playlist)
                status = get_playlist_status(playlist)
                print("status:", status)
                if status != pl.status:
                    pl.status = status
                    pl.save()
            else:
                self.new_playlist(playlist)


class SpotifyUserCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=400)
    refresh_token = models.CharField(max_length=400)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"(email={self.user.email})"

    @property
    def has_expired(self):
        if not self.expires_at:
            return True

        return self.expires_at <= timezone.now()

    def refresh(self):
        sp = get_spotify_oauth(scopes)
        token_info = sp.refresh_access_token(self.refresh_token)
        self.access_token = token_info["access_token"]
        self.refresh_token = token_info["refresh_token"]
        self.expires_at = datetime.datetime.fromtimestamp(
            token_info["expires_at"], datetime.timezone.utc
        )
        self.save()

    def check_expired(self):
        if self.has_expired:
            self.refresh()
