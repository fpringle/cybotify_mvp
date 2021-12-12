__all__ = [
    "SpotifyManager",
    "DEFAULT_SCOPES",
]

from .client import Spotify
from .oauth2 import SpotifyClientCredentials, SpotifyOAuth

DEFAULT_SCOPES = [
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


class SpotifyManager:
    def __init__(
        self, id, secret, redirect_uri, scopes=None, requests_timeout=10, retries=10
    ):
        self.client_id = id
        self.client_secret = secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or DEFAULT_SCOPES
        self.requests_timeout = requests_timeout
        self.retries = retries
        self.client_credentials = SpotifyClientCredentials(
            client_id=id, client_secret=secret, requests_timeout=requests_timeout
        )
        self.oauth = SpotifyOAuth(
            client_id=id,
            client_secret=secret,
            redirect_uri=redirect_uri,
            requests_timeout=requests_timeout,
            scope=" ".join(self.scopes),
        )
        self.app_client = Spotify(
            auth_manager=self.client_credentials,
            requests_timeout=requests_timeout,
            retries=retries,
        )

    def user_client(self, access_token, requests_timeout=None, retries=None):
        if retries is None:
            retries = self.retries
        if requests_timeout is None:
            requests_timeout = self.requests_timeout
        return Spotify(
            auth=access_token,
            requests_timeout=requests_timeout,
            retries=retries,
        )

    def authorize_url(self, state):
        return self.oauth.get_authorize_url(state)

    def get_tokens(self, code):
        return self.oauth.get_access_token(code)

    def refresh_tokens(self, refresh_token):
        return self.oauth.refresh_access_token(refresh_token)

    @staticmethod
    def _next_until_end(client, response):
        items = response["items"]
        while response["next"]:
            response = client.next(response)
            items.extend(response["items"])
        return items

    def get_playlists(self, access_token):
        client = self.user_client(access_token)
        response = client.current_user_playlists(limit=50)
        return SpotifyManager._next_until_end(client, response)

    @staticmethod
    def get_playlist_status(playlist_data):
        if playlist_data.get("public", False):
            return "PU"
        elif playlist_data.get("collaborative", False):
            return "CO"
        else:
            return "PR"

    @staticmethod
    def get_playlist_tracks(client, playlist_id):
        response = client.playlist_items(
            playlist_id,
            limit=50,
            fields="items(track(id,name,artists(name),album(name),is_local)),next",
        )
        results = SpotifyManager._next_until_end(client, response)
        return [
            track["track"]
            for track in results
            if not track["track"].get("is_local", True)
        ]

    def get_track_features(self, track_ids):
        track_features = []
        while track_ids:
            response = self.app_client.audio_features(track_ids[:100])
            track_ids = track_ids[100:]
            track_features.extend(response)

        return track_features
