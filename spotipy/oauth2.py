__all__ = [
    "SpotifyClientCredentials",
    "SpotifyOAuth",
    "SpotifyOauthError",
    "SpotifyStateError",
]

import base64
import logging
import os
import time
import warnings

import requests

# Workaround to support both python 2 & 3
import six
import six.moves.urllib.parse as urllibparse
from six.moves.urllib_parse import parse_qsl, urlparse

from spotipy.cache_handler import MemoryCacheHandler
from spotipy.util import CLIENT_CREDS_ENV_VARS, normalize_scope

logger = logging.getLogger(__name__)


class SpotifyOauthError(Exception):
    """Error during Auth Code or Implicit Grant flow"""

    def __init__(self, message, error=None, error_description=None, *args, **kwargs):
        self.error = error
        self.error_description = error_description
        self.__dict__.update(kwargs)
        super().__init__(message, *args, **kwargs)


class SpotifyStateError(SpotifyOauthError):
    """The state sent and state recieved were different"""

    def __init__(
        self,
        local_state=None,
        remote_state=None,
        message=None,
        error=None,
        error_description=None,
        *args,
        **kwargs,
    ):
        if not message:
            message = "Expected " + local_state + " but recieved " + remote_state
        super(SpotifyOauthError, self).__init__(
            message, error, error_description, *args, **kwargs
        )


def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(str(client_id + ":" + client_secret).encode("ascii"))
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}


def _ensure_value(value, env_key):
    env_val = CLIENT_CREDS_ENV_VARS[env_key]
    _val = value or os.getenv(env_val)
    if _val is None:
        msg = "No {}. Pass it or set a {} environment variable.".format(
            env_key,
            env_val,
        )
        raise SpotifyOauthError(msg)
    return _val


class SpotifyAuthBase:
    def __init__(self, requests_session):
        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                from requests import api

                self._session = api

    def _normalize_scope(self, scope):
        return normalize_scope(scope)

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, val):
        self._client_id = _ensure_value(val, "client_id")

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, val):
        self._client_secret = _ensure_value(val, "client_secret")

    @property
    def redirect_uri(self):
        return self._redirect_uri

    @redirect_uri.setter
    def redirect_uri(self, val):
        self._redirect_uri = _ensure_value(val, "redirect_uri")

    @staticmethod
    def is_token_expired(token_info):
        now = int(time.time())
        return token_info["expires_at"] - now < 60

    @staticmethod
    def _is_scope_subset(needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split()) if needle_scope else set()
        haystack_scope = set(haystack_scope.split()) if haystack_scope else set()
        return needle_scope <= haystack_scope

    def _handle_oauth_error(self, http_error):
        response = http_error.response
        try:
            error_payload = response.json()
            error = error_payload.get("error")
            error_description = error_payload.get("error_description")
        except ValueError:
            # if the response cannnot be decoded into JSON (which raises a ValueError),
            # then try do decode it into text

            # if we receive an empty string (which is falsy), then replace it with `None`
            error = response.txt or None
            error_description = None

        raise SpotifyOauthError(
            f"error: {error}, error_description: {error_description}",
            error=error,
            error_description=error_description,
        )

    def __del__(self):
        """Make sure the connection (pool) gets closed"""
        if isinstance(self._session, requests.Session):
            self._session.close()


class SpotifyClientCredentials(SpotifyAuthBase):
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        proxies=None,
        requests_session=True,
        requests_timeout=None,
    ):
        """
        Creates a Client Credentials Flow Manager.

        The Client Credentials flow is used in server-to-server authentication.
        Only endpoints that do not access user information can be accessed.
        This means that endpoints that require authorization scopes cannot be accessed.
        The advantage, however, of this authorization flow is that it does not require any
        user interaction

        You can either provide a client_id and client_secret to the
        constructor or set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET
        environment variables

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * proxies: Optional, proxy for the requests library to route through
             * requests_session: A Requests session
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds

        """

        super().__init__(requests_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.cache_handler = MemoryCacheHandler()

    def get_access_token(self, as_dict=True):
        """
        If a valid access token is in memory, returns it
        Else feches a new token and returns it

            Parameters:
            - as_dict - a boolean indicating if returning the access token
                as a token_info dictionary, otherwise it will be returned
                as a string.
        """
        if as_dict:
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly.",
                DeprecationWarning,
                stacklevel=2,
            )

        token_info = self.cache_handler.get_cached_token()
        if token_info and not self.is_token_expired(token_info):
            return token_info if as_dict else token_info["access_token"]

        token_info = self._request_access_token()
        token_info = self._add_custom_values_to_token_info(token_info)
        self.cache_handler.save_token_to_cache(token_info)
        return token_info if as_dict else token_info["access_token"]

    def _request_access_token(self):
        """Gets client credentials access token"""
        payload = {"grant_type": "client_credentials"}

        headers = _make_authorization_headers(self.client_id, self.client_secret)

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL,
            headers,
            payload,
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                verify=True,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            return token_info
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        return token_info


class SpotifyOAuth(SpotifyAuthBase):
    """
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    """

    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        redirect_uri=None,
        state=None,
        scope=None,
        proxies=None,
        show_dialog=False,
        requests_session=True,
        requests_timeout=None,
    ):
        """
        Creates a SpotifyOAuth object

        Parameters:
             * client_id: Must be supplied or set as environment variable
             * client_secret: Must be supplied or set as environment variable
             * redirect_uri: Must be supplied or set as environment variable
             * state: Optional, no verification is performed
             * scope: Optional, either a list of scopes or comma separated string of scopes.
                      e.g, "playlist-read-private,playlist-read-collaborative"
             * proxies: Optional, proxy for the requests library to route through
             * show_dialog: Optional, interpreted as boolean
             * requests_session: A Requests session
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
        """

        super().__init__(requests_session)

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.scope = self._normalize_scope(scope)

        self.proxies = proxies
        self.requests_timeout = requests_timeout
        self.show_dialog = show_dialog

    def validate_token(self, token_info):
        if token_info is None:
            return None

        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
            self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(token_info["refresh_token"])

        return token_info

    def get_authorize_url(self, state=None):
        """Gets the URL to use to authorize this app"""
        payload = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if self.scope:
            payload["scope"] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload["state"] = state
        if self.show_dialog:
            payload["show_dialog"] = True

        urlparams = urllibparse.urlencode(payload)

        return f"{self.OAUTH_AUTHORIZE_URL}?{urlparams}"

    def parse_response_code(self, url):
        """Parse the response code in the given response url

        Parameters:
            - url - the response url
        """
        _, code = self.parse_auth_response_url(url)
        if code is None:
            return url
        else:
            return code

    @staticmethod
    def parse_auth_response_url(url):
        query_s = urlparse(url).query
        form = dict(parse_qsl(query_s))
        if "error" in form:
            raise SpotifyOauthError(
                "Received error from auth server: " "{}".format(form["error"]),
                error=form["error"],
            )
        return tuple(form.get(param) for param in ["state", "code"])

    def _make_authorization_headers(self):
        return _make_authorization_headers(self.client_id, self.client_secret)

    def get_access_token(self, code, as_dict=True):
        """Gets the access token for the app given the code

        Parameters:
            - code - the response code
            - as_dict - a boolean indicating if returning the access token
                        as a token_info dictionary, otherwise it will be returned
                        as a string.
        """
        if as_dict:
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly.",
                DeprecationWarning,
                stacklevel=2,
            )

        payload = {
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }
        if self.scope:
            payload["scope"] = self.scope
        if self.state:
            payload["state"] = self.state

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL,
            headers,
            payload,
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                verify=True,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            return token_info if as_dict else token_info["access_token"]
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def refresh_access_token(self, refresh_token):
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = self._make_authorization_headers()

        logger.debug(
            "sending POST request to %s with Headers: %s and Body: %r",
            self.OAUTH_TOKEN_URL,
            headers,
            payload,
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            if "refresh_token" not in token_info:
                token_info["refresh_token"] = refresh_token
            return token_info
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        token_info["scope"] = self.scope
        return token_info
