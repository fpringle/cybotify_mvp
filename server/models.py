import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from spotipy.oauth2 import SpotifyOAuth

from .spotify_client_info import get_spotify_oauth
from .util import random_string

class RegistrationState(models.Model):
    state_string = models.CharField(max_length=16)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.state_string = self.__class__.unique_random_string(16)
        self.state_string = random_string(16)

    @classmethod
    def unique_random_string(cls, length):
        string = random_string(16)
        while cls.objects.filter(state_string = string).exists():
            string = random_string(16)
        return string

    class Meta:
        verbose_name = "User pending registration"
        verbose_name_plural = "Users pending registration"

class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    spotify_id = models.CharField(max_length=64)

    def __str__(self):
        return f"(email={self.user.email}, spotifyID={self.spotify_id})"

class SpotifyUserCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
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

    def refresh(self, save=True):
        sp = get_spotify_oauth()
        token_info = sp.refresh_access_token(self.refresh_token)
        self.access_token = token_info["access_token"]
        self.refresh_token = token_info["refresh_token"]
        self.expires_at = datetime.datetime.fromtimestamp(token_info["expires_at"], datetime.timezone.utc)
        if save:
            self.save()

    def check_expired(self, save=True):
        if self.has_expired:
            self.refresh(save)

class UserPlaylist(models.Model):
    spotify_id = models.CharField(max_length=64)
    snapshot_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    last_updated = models.DateTimeField()

    def __str__(self):
        return f"(name={self.name}, user={self.user.user.email}, spotifyID={self.spotify_id})"

class Track(models.Model):
    spotify_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    artists = models.CharField(max_length=128)
    album = models.CharField(max_length=64)
    playlist = models.ManyToManyField(UserPlaylist)

    def __str__(self):
        return f"(name={self.name}, artists={self.artists}, spotifyID={self.spotify_id})"

class TrackFeatures(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE, primary_key=True)

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
