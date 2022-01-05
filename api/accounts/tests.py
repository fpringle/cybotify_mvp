from unittest import mock

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone

from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials, User  # noqa

DEFAULT_USERNAME = "user"
DEFAULT_EMAIL = "user@user.com"
DEFAULT_FIRSTNAME = "firstname"
DEFAULT_LASTNAME = "lastname"
DEFAULT_SPOTIFY_ID = "spotify_id"
DEFAULT_PASSWORD = "password"
DEFAULT_ACCESS_TOKEN = "ACCESS_TOKEN"
DEFAULT_REFRESH_TOKEN = "REFRESH_TOKEN"
DEFAULT_EXPIRES_AT = timezone.datetime(2021, 12, 1, tzinfo=timezone.utc)


# fixtures
def create_user_with_spotify_user_and_credentials(
    username=DEFAULT_USERNAME,
    email=DEFAULT_EMAIL,
    first_name=DEFAULT_FIRSTNAME,
    last_name=DEFAULT_LASTNAME,
    password=DEFAULT_PASSWORD,
    spotify_id=DEFAULT_SPOTIFY_ID,
    hash_password=False,
    access_token=DEFAULT_ACCESS_TOKEN,
    refresh_token=DEFAULT_REFRESH_TOKEN,
    expires_at=DEFAULT_EXPIRES_AT,
):
    user = User.objects.create(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=make_password(password) if hash_password else password,
    )
    spotify_user = SpotifyUser.objects.create(
        user=user,
        spotify_id=spotify_id,
    )
    credentials = SpotifyUserCredentials.objects.create(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    return user, spotify_user, credentials


class RegistrationStateTestCase(TestCase):
    """
    Test model RegistrationState and its manager class RegistrationStateManager
    """

    def setUp(self):
        """
        Clear the db for each test
        """
        RegistrationState.objects.all().delete()

    def test_state_strings_are_unique(self):
        """
        Check if the randomly-generated state strings are guaranteed unique
        By limiting the length of the strings to 2, the total nummber of unique
        strings is 62 * 62 = 3844. If we do 250 iterations, by the birthday problem
        (https://en.wikipedia.org/wiki/Birthday_problem), the chances of 2 strings
        being equal (with normal random choices) is 99.97%. So if none of these
        are equal, we can be certain that the uniqueness method is working.
        """
        strings = set()
        for _ in range(250):
            state_string = RegistrationState.objects.unique_random_string(2)
            self.assertNotIn(state_string, strings)
            strings.add(state_string)
            reg = RegistrationState.objects.create_state()
            reg.state_string = state_string
            reg.save()

    def test_drop_older_than(self):
        """
        Test that RegistrationStateManager.drop_before works as intended
        """

        def strings():
            return sorted(reg.state_string for reg in RegistrationState.objects.all())

        self.assertEqual(strings(), [])

        times = [(2021, 12, 14, 11), (2021, 12, 14, 12), (2021, 12, 14, 13)]
        times = [timezone.datetime(*args, tzinfo=timezone.utc) for args in times]
        for time in times:
            reg = RegistrationState.objects.create_state()
            reg.state_string = str(time.hour)
            reg.created_at = time
            reg.save()

        self.assertEqual(strings(), ["11", "12", "13"])
        RegistrationState.objects.drop_before(times[2])
        self.assertEqual(strings(), ["13"])

    def test_created_at_autonow(self):
        """
        RegistrationState.created_at should be automatically set now on creation
        """
        now = timezone.now()
        reg = RegistrationState.objects.create_state()
        self.assertAlmostEqual(now.timestamp(), reg.created_at.timestamp(), places=2)


def fake_refresh_token(refresh_token):
    return {
        "access_token": DEFAULT_ACCESS_TOKEN,
        "refresh_token": DEFAULT_REFRESH_TOKEN,
        "expires_at": (timezone.now() + timezone.timedelta(hours=1)).timestamp(),
    }


class UserCredentialsTestCase(TestCase):
    def setUp(self):
        _user = create_user_with_spotify_user_and_credentials()
        self.user, self.spotify_user, self.credentials = _user

    def test_expired(self):
        self.assertTrue(self.user.credentials.has_expired)

    @mock.patch(
        "api.accounts.SpotifyManager.refresh_tokens", side_effect=fake_refresh_token
    )
    def test_refresh(self, mock_refresh):
        self.user.credentials.refresh()
        self.assertFalse(self.user.credentials.has_expired)
