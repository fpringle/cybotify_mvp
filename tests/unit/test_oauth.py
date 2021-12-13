import io
import unittest

import six.moves.urllib.parse as urllibparse

from spotipy import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError

try:
    import unittest.mock as mock
except ImportError:
    from unittest import mock

patch = mock.patch
DEFAULT = mock.DEFAULT


def _make_fake_token(expires_at, expires_in, scope):
    return dict(
        expires_at=expires_at,
        expires_in=expires_in,
        scope=scope,
        token_type="Bearer",
        refresh_token="REFRESH",
        access_token="ACCESS",
    )


def _fake_file():
    return mock.Mock(spec_set=io.FileIO)


def _token_file(token):
    fi = _fake_file()
    fi.read.return_value = token
    return fi


def _make_oauth(*args, **kwargs):
    return SpotifyOAuth("CLID", "CLISEC", "REDIR", "STATE", *args, **kwargs)


class TestSpotifyOAuthGetAuthorizeUrl(unittest.TestCase):
    def test_get_authorize_url_doesnt_pass_state_by_default(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR")

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn("state", parsed_qs)

    def test_get_authorize_url_passes_state_from_constructor(self):
        state = "STATE"
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", state)

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs["state"][0], state)

    def test_get_authorize_url_passes_state_from_func_call(self):
        state = "STATE"
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", "NOT STATE")

        url = oauth.get_authorize_url(state=state)

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs["state"][0], state)

    def test_get_authorize_url_does_not_show_dialog_by_default(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR")

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertNotIn("show_dialog", parsed_qs)

    def test_get_authorize_url_shows_dialog_when_requested(self):
        oauth = SpotifyOAuth("CLID", "CLISEC", "REDIR", show_dialog=True)

        url = oauth.get_authorize_url()

        parsed_url = urllibparse.urlparse(url)
        parsed_qs = urllibparse.parse_qs(parsed_url.query)
        self.assertTrue(parsed_qs["show_dialog"])


class TestSpotifyClientCredentials(unittest.TestCase):
    def test_spotify_client_credentials_get_access_token(self):
        oauth = SpotifyClientCredentials(client_id="ID", client_secret="SECRET")
        with self.assertRaises(SpotifyOauthError) as error:
            oauth.get_access_token()
        self.assertEqual(error.exception.error, "invalid_client")
