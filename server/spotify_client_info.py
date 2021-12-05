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

def get_spotify_client(scopes, requests_timeout=10, requests_retries=10):
    auth = get_spotify_oauth(scopes, requests_timeout)
    return Spotify(auth_manager=auth, requests_retries=requests_retries)
