""" Shows a user's playlists (need to be authenticated via oauth) """

__all__ = ["CLIENT_CREDS_ENV_VARS"]

import logging

LOGGER = logging.getLogger(__name__)

CLIENT_CREDS_ENV_VARS = {
    "client_id": "SPOTIPY_CLIENT_ID",
    "client_secret": "SPOTIPY_CLIENT_SECRET",
    "redirect_uri": "SPOTIPY_REDIRECT_URI",
}


def normalize_scope(scope):
    if scope:
        if isinstance(scope, str):
            scopes = scope.split(",")
        elif isinstance(scope, list) or isinstance(scope, tuple):
            scopes = scope
        else:
            raise Exception(
                "Unsupported scope value, please either provide a list of scopes, "
                "or a string of scopes separated by commas"
            )
        return " ".join(sorted(scopes))
    else:
        return None
