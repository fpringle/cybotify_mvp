import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from music.models import UserPlaylist

from . import SpotifyManager
from .util import random_string


class RegistrationState(models.Model):
    state_string = models.CharField(max_length=16)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_string = self.__class__.unique_random_string(16)

    @classmethod
    def unique_random_string(cls, length):
        string = random_string(length)
        while cls.objects.filter(state_string=string).exists():
            string = random_string(length)
        return string

    class Meta:
        verbose_name = "User pending registration"
        verbose_name_plural = "Users pending registration"

    @classmethod
    def drop_before(cls, date_time):
        if timezone.is_naive(date_time):
            date_time = timezone.make_aware
        cls.objects.filter(created_at__lt=date_time).delete()

    @classmethod
    def drop_older_than(cls, time_delta):
        dt = timezone.now() - time_delta
        cls.drop_before(dt)


class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    spotify_id = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return f"(email={self.user.email}, spotifyID={self.spotify_id})"

    def update_playlists(self):
        self.user.credentials.check_expired()
        playlists = SpotifyManager.get_playlists(self.user.credentials.access_token)
        for playlist in playlists:
            UserPlaylist.create_or_update(playlist, self)

        playlist_ids = [pl["id"] for pl in playlists if "id" in pl]
        to_remove = self.userplaylist_set.filter(~models.Q(spotify_id__in=playlist_ids))
        self.userplaylist_set.remove(*to_remove)

    @property
    def public_playlists(self):
        return self.userplaylist_set.filter(status="PU")

    @property
    def private_playlists(self):
        return self.userplaylist_set.filter(status="PR")

    @property
    def collaborative_playlists(self):
        return self.userplaylist_set.filter(status="CO")


class SpotifyUserCredentials(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="credentials"
    )
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
        token_info = SpotifyManager.refresh_tokens(self.refresh_token)
        self.access_token = token_info["access_token"]
        self.refresh_token = token_info["refresh_token"]
        self.expires_at = datetime.datetime.fromtimestamp(
            token_info["expires_at"], datetime.timezone.utc
        )
        self.save()

    def check_expired(self):
        if self.has_expired:
            self.refresh()
