from django.test import TestCase
from django.utils import timezone

from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials, User  # noqa


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
