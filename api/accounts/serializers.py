from rest_framework import serializers

from .models import SpotifyUser, User


class SpotifyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyUser
        fields = ["id", "spotify_id"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "spotify_user"]

    spotify_user = SpotifyUserSerializer(source="spotifyuser", read_only=True)
