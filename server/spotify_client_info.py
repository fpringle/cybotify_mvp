import environ

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from django.conf import settings

env = environ.Env()
environ.Env.read_env(settings.BASE_DIR / "cybotify" / ".env")

def get_client_info():
    return (
        env("SPOTIFY_CLIENT_ID"),
        env("SPOTIFY_CLIENT_SECRET"),
        env("SPOTIFY_REDIRECT_URI"),
    )

scopes = [
    "user-read-private",
    "user-read-email",
    "user-library-modify",
    "user-follow-read",
    "user-top-read",
    "playlist-modify-private",
    "playlist-modify-public",
    "playlist-read-collaborative",
    "playlist-read-private",
]

def get_spotify_oauth(scopes, requests_timeout=10):
    client_id, client_secret, redirect_uri = get_client_info()
    scope = scopes if isinstance(scopes, str) else " ".join(scopes)
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        requests_timeout=requests_timeout,
        scope=scope,
        open_browser=False,
    )

def get_spotify_client_credentials(requests_timeout=10):
    client_id, client_secret, _ = get_client_info()
    return SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
        requests_timeout=requests_timeout
    )

def get_spotify_client(requests_timeout=10, retries=10):
    auth = get_spotify_client_credentials(requests_timeout)
    return Spotify(auth_manager=auth, requests_timeout=requests_timeout, retries=retries)

def get_spotify_user_client(access_token, requests_timeout=10, retries=10):
    return Spotify(auth=access_token, requests_timeout=requests_timeout, retries=retries)

def get_all_playlists(spotify_user_client):
    offset = 0
    playlists = []
    while True:
        response = spotify_user_client.current_user_playlists(limit=50, offset=offset)
        playlists.extend(response["items"])
        offset += len(response["items"])
        if not response["next"]:
            break

    return playlists

def get_all_playlist_tracks(sp, playlist_id):
    offset = 0
    info = []

    while True:
        response = sp.playlist_items(
            playlist_id,
            offset=offset,
            limit=50,
            fields=f"items(track(id,name,artists(name),album(name),is_local)),next",
        )

        info.extend(
            tr["track"] for tr in response["items"] if not tr["track"].get("is_local", True)
        )
        offset = offset + len(response["items"])
        if not response["next"]:
            break

    return info

def get_all_track_features(sp, tracks):
    track_features = []
    while tracks:
        request = tracks[:100]
        tracks = tracks[100:]
        response = sp.audio_features(request)
        track_features.extend(response)

    return track_features
