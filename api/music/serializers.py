from rest_framework import serializers

from .models import Track, TrackFeatures, UserPlaylist


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ["id", "spotify_id", "name", "artists", "album"]

    artists = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        source="artist_list",
    )


class TrackFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackFeatures
        fields = [
            "acousticness",
            "danceability",
            "energy",
            "instrumentalness",
            "key",
            "liveness",
            "loudness",
            "mode",
            "speechiness",
            "tempo",
            "time_signature",
            "valence",
        ]


class TrackWithFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ["id", "spotify_id", "name", "artists", "album", "features"]

    features = TrackFeaturesSerializer(source="track_features", read_only=True)


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlaylist
        fields = ["id", "spotify_id", "name", "owner", "last_updated", "status"]


class PlaylistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlaylist
        fields = [
            "id",
            "spotify_id",
            "name",
            "owner",
            "last_updated",
            "status",
            "tracks",
        ]

    tracks = TrackSerializer(source="track_set", many=True, read_only=True)


class PlaylistFeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPlaylist
        fields = [
            "id",
            "spotify_id",
            "name",
            "owner",
            "last_updated",
            "status",
            "tracks",
        ]

    tracks = TrackWithFeaturesSerializer(source="track_set", many=True, read_only=True)
