from django.test import TestCase

from .models import Track, TrackFeatures, UserPlaylist  # noqa


class TrackTestCase(TestCase):
    def setUp(self):
        """
        Clear the db for each test
        """
        Track.objects.all().delete()

    def test_artist_list(self):
        """
        Test we're encoding and decoding the artist list correctly
        """
        track = Track.objects.create(artists="artist1 =|AND|= artist2")
        artist_list = track.artist_list
        artists_comma_separated = track.artists_comma_separated

        self.assertEqual(artist_list, ["artist1", "artist2"])
        self.assertEqual(artists_comma_separated, "artist1, artist2")
