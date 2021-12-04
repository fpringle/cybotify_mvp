from django.db import models
from django.contrib.auth.models import User


class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    spotify_id = models.CharField(max_length=64)

class SpotifyUserCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    access_token = models.CharField(max_length=400)
    refresh_token = models.CharField(max_length=400)
    expires_at = models.DateTimeField()

class UserPlaylist(models.Model):
    spotify_id = models.CharField(max_length=64)
    snapshot_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE)
    last_updated = models.DateTimeField()

class Track(models.Model):
    spotify_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    artists = models.CharField(max_length=128)
    album = models.CharField(max_length=64)
    playlist = models.ManyToManyField(UserPlaylist)

class TrackFeatures(models.Model):
    track = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

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
