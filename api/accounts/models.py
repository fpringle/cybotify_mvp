import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from api.music.models import UserPlaylist

from . import SpotifyManager
from .util import random_string


class RegistrationStateManager(models.Manager):
    def unique_random_string(self, length):
        string = random_string(length)
        while self.filter(state_string=string).exists():
            string = random_string(length)
        return string

    def create_state(self, *args, **kwargs):
        state_string = self.unique_random_string(16)
        kwargs["state_string"] = state_string
        return self.create(*args, **kwargs)

    def drop_before(self, date_time):
        if timezone.is_naive(date_time):
            date_time = timezone.make_aware
        self.filter(created_at__lt=date_time).delete()

    def drop_older_than(self, time_delta):
        dt = timezone.now() - time_delta
        self.drop_before(dt)


class RegistrationState(models.Model):
    state_string = models.CharField(max_length=16, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = RegistrationStateManager()

    class Meta:
        verbose_name = "User pending registration"
        verbose_name_plural = "Users pending registration"


class SpotifyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    spotify_id = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return f"(email={self.user.email}, spotifyID={self.spotify_id})"

    def update_playlists(self):
        self.user.credentials.check_expired()
        playlists = SpotifyManager.get_playlists(self.user.credentials.access_token)
        for position, playlist in enumerate(playlists, 0):
            UserPlaylist.objects.create_or_update(playlist, self, position)

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

        return self.expires_at <= timezone.now() + timezone.timedelta(minutes=1)

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
