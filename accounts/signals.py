from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import SpotifyUser


@receiver(pre_delete, sender=SpotifyUser)
def delete_spotify_user(sender, instance, using, **kwargs):
    if instance.user and instance.user.spotifyusercredentials:
        instance.user.spotifyusercredentials.delete()
