import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from spotipy.oauth2 import SpotifyOAuth

from .spotify_client_info import (
    get_spotify_oauth,
    get_spotify_user_client,
    get_all_playlists,
    get_all_playlist_tracks,
    get_spotify_client,
    scopes,
)
from .util import random_string


class RegistrationState(models.Model):
    state_string = models.CharField(max_length=16)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

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
        print(playlist_data)
        playlist = UserPlaylist.objects.create(
            spotify_id=playlist_data["id"],
            name=playlist_data["name"],
            #snapshot_id=playlist_data["snapshot_id"],
            user=self,
        )
        playlist.save()
        #playlist.update_tracks()

    def update_playlists(self):
        self.user.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(self.user.spotifyusercredentials.access_token)
        playlists = get_all_playlists(sp)
        # drop playlists that are no longer present
        for playlist in playlists:
            spotify_id = playlist["id"]
            if UserPlaylist.objects.filter(spotify_id=spotify_id).exists():
                #pl = UserPlaylist.objects.get(spotify_id=spotify_id)
                #pl.check_update()
                pass
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


class UserPlaylist(models.Model):
    spotify_id = models.CharField(max_length=256)
    snapshot_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def get_latest_snapshot(self):
        su = self.user.user
        su.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(su.spotifyusercredentials.access_token)
        return sp.playlist(self.spotify_id, fields="snapshot_id")["snapshot_id"]

    def update_tracks(self):
        su = self.user.user
        su.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(su.spotifyusercredentials.access_token)
        tracks = get_all_playlist_tracks(sp, self.spotify_id)
        for track_data in tracks:
            if Track.objects.filter(spotify_id=track_data["id"]).exists():
                track = Track.objects.get(spotify_id=track_data["id"])
                track.get_features()
                if not self.track_set.filter(pk=track.pk).exists():
                    self.track_set.add(track)
                continue
            track = Track.objects.create(
                spotify_id=track_data["id"],
                name=track_data["name"],
                artists=" =|AND|= ".join(
                    artist["name"] for artist in track_data["artists"]
                ),
                album=track_data["album"]["name"],
            )
            track.get_features()
            track.save()
            self.track_set.add(track)

        self.save()

    def check_update(self):
        current = self.get_latest_snapshot()
        if current == self.snapshot_id:
            print("  Already up to date")
            return
        print(f"Playlist {self.name} - checking for updates (DB snapshot ID {self.snapshot_id})")
        print(f"  Spotify latest snapshot id is {current}, updating")
        self.snapshot_id = current
        #self.save()
        self.update_tracks()

    def __str__(self):
        return f"(name={self.name}, user={self.user.user.email}, spotifyID={self.spotify_id})"


class Track(models.Model):
    spotify_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    artists = models.CharField(max_length=256)
    album = models.CharField(max_length=256)
    playlist = models.ManyToManyField(UserPlaylist)

    @property
    def artist_list(self):
        return self.artists.split(" =|AND|= ")

    def get_features(self):
        if hasattr(self, "track_features"):
            return
        print(f"getting features for track '{self.name}'")
        sp = get_spotify_client()
        track_features_data = sp.audio_features(self.spotify_id)[0]
        self.track_features = TrackFeatures(
            track=self,
            acousticness=track_features_data["acousticness"],
            danceability=track_features_data["danceability"],
            energy=track_features_data["energy"],
            instrumentalness=track_features_data["instrumentalness"],
            key=track_features_data["key"],
            liveness=track_features_data["liveness"],
            loudness=track_features_data["loudness"],
            mode=track_features_data["mode"],
            speechiness=track_features_data["speechiness"],
            tempo=track_features_data["tempo"],
            time_signature=track_features_data["time_signature"],
            valence=track_features_data["valence"],
        )
        print(self.track_features)
        self.track_features.save()
        self.save()

    def __str__(self):
        return (
            f"(name={self.name}, artists={self.artists}, spotifyID={self.spotify_id})"
        )


class TrackFeatures(models.Model):
    track = models.OneToOneField(
        Track, on_delete=models.CASCADE, related_name="track_features"
    )

    class Mode(models.IntegerChoices):
        MAJOR = 1
        MINOR = 0

    acousticness = models.FloatField()
    danceability = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    key = models.SmallIntegerField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.IntegerField(choices=Mode.choices)
    speechiness = models.FloatField()
    tempo = models.FloatField()
    time_signature = models.SmallIntegerField()
    valence = models.FloatField()

    def __str__(self):
        return self.track.__str__()
