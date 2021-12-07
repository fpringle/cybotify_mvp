from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

from music.models import UserPlaylist

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


def get_track_features(track, fields=None):
    fields = fields or ALL_FIELDS[:]
    if not hasattr(track, "track_features"):
        return {}
    features = track.track_features
    return {
        field: getattr(features, field) for field in fields if hasattr(features, field)
    }


def get_playlist_average_features(playlist, fields=None):
    tracks = playlist.track_set.all()
    fields = fields or ALL_FIELDS[:]
    track_features = [get_track_features(track, fields) for track in tracks]

    track_features = {
        field: [features[field] for features in track_features if field in features]
        for field in fields
    }

    track_features = {
        field: sum(values) / len(values)
        for field, values in track_features.items()
        if values
    }

    return {
        "name": playlist.name,
        "length": len(tracks),
        "features": track_features,
    }

def get_playlist_features_by_db_id(id, fields=None):
    playlist = UserPlaylist.objects.filter(pk=id).get()
    return get_playlist_average_features(playlist, fields)

def get_playlist_features_by_spotify_id(spotify_id, fields=None):
    playlist = UserPlaylist.objects.filter(spotify_id=spotify_id).get()
    return get_playlist_average_features(playlist, fields)


def get_playlist_features(request, playlist_id):
    fields = request.GET.get("fields")
    if fields:
        fields = [field for field in fields.split(",") if field in ALL_FIELDS]
    else:
        fields = ALL_FIELDS[:]

    features = get_playlist_features_by_db_id(playlist_id, fields)
    return JsonResponse(features)

@login_required
def playlist_detail(request, playlist_id):
    playlist = UserPlaylist.objects.filter(pk=playlist_id).get()
    if request.user != playlist.user.user:
        return HttpResponseForbidden("That's not your playlist!")

    playlist.check_update()
    context = {
        "playlist": playlist,
        "features": get_playlist_average_features(playlist),
    }

    return render(request, '', context)