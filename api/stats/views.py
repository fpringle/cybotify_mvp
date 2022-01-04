from django_pandas.io import read_frame
from pandas.core.frame import DataFrame
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.music.models import TrackFeatures, UserPlaylist

FLOAT_FIELDS = [
    "danceability",
    "energy",
    "key",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
]

INTEGER_FIELDS = [
    "key",
    "time_signature",
]

ENUM_FIELDS = [
    "mode",
]

ALL_FIELDS = FLOAT_FIELDS + INTEGER_FIELDS + ENUM_FIELDS


def get_playlist_features_df(playlist) -> DataFrame:
    playlist.update_tracks()
    qs = TrackFeatures.objects.filter(track__playlist=playlist)
    return read_frame(qs).rename(columns={"track": "id"})


def get_playlist_average_features(playlist, fields=None):
    fields = fields or ALL_FIELDS[:]
    df = get_playlist_features_df(playlist)
    feature_means = df[fields].mean(axis=0).to_dict()
    feature_stdevs = df[fields].std(axis=0).to_dict()
    track_features = df.to_dict("records")
    return {
        "name": playlist.name,
        "features": feature_means,
        "feature_stdevs": feature_stdevs,
        "track_features": track_features,
    }


def get_playlist_features_by_db_id(id, fields=None):
    playlist = UserPlaylist.objects.filter(pk=id).get()
    return get_playlist_average_features(playlist, fields)


def get_playlist_features_by_spotify_id(spotify_id, fields=None):
    playlist = UserPlaylist.objects.filter(spotify_id=spotify_id).get()
    return get_playlist_average_features(playlist, fields)


@api_view(["GET"])
def get_playlist_features(request, playlist_id):
    fields = request.GET.get("fields")
    if fields:
        fields = [field for field in fields.split(",") if field in ALL_FIELDS]
    else:
        fields = ALL_FIELDS[:]

    features = get_playlist_features_by_db_id(playlist_id, fields)
    return Response(features)
