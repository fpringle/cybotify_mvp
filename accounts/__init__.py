import environ
from django.conf import settings

from spotipy import SpotifyManager as SM

env = environ.Env()
environ.Env.read_env(settings.BASE_DIR / "cybotify" / ".env")

SpotifyManager = SM(
    env("SPOTIFY_CLIENT_ID"),
    env("SPOTIFY_CLIENT_SECRET"),
    env("SPOTIFY_REDIRECT_URI"),
)
