import random
import time
from unittest import skipIf

import tqdm
from django.test import TestCase

from music.models import Track, TrackFeatures, UserPlaylist  # noqa

from .test_data import playlist_lengths
from .views import ALL_FIELDS

number_runs = 5000
number_playlists = 1000
number_tracks = 100000

skip_long_tests = True


class FeaturesLookupSpeedTestCase(TestCase):
    @skipIf(skip_long_tests, "Skipping long test")
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create tracks with features
        print("create tracks + features")
        tracks = [Track(pk=i, spotify_id=str(i)) for i in tqdm.trange(number_tracks)]
        print("bulk create tracks")
        Track.objects.bulk_create(tracks, batch_size=100000)
        track_features = [
            TrackFeatures(
                track_id=i,
                acousticness=random.random(),
                danceability=random.random(),
                energy=random.random(),
                instrumentalness=random.random(),
                key=random.random(),
                liveness=random.random(),
                loudness=random.random(),
                mode=random.random(),
                speechiness=random.random(),
                tempo=random.random(),
                time_signature=random.random(),
                valence=random.random(),
            )
            for i in tqdm.trange(number_tracks)
        ]

        print("bulk create track features")
        TrackFeatures.objects.bulk_create(track_features, batch_size=100000)

        # create playlists
        print("create playlists")
        for i in tqdm.trange(number_playlists):
            playlist = UserPlaylist.objects.create(pk=i, spotify_id=str(i))
            tracks_in_playlist = random.choice(playlist_lengths)
            tracks = random.sample(range(number_tracks), tracks_in_playlist)
            playlist.track_set.set(tracks)

        print("# of playlists:", UserPlaylist.objects.count())
        print("# of tracks:", Track.objects.count())
        print("# of runs:", number_runs)

    def setUp(self):
        random.seed(0)

    @classmethod
    def _method_1(cls, playlist):
        query_fields = ["track_features__" + field for field in ["id"] + ALL_FIELDS]
        qs = playlist.track_set.values(*query_fields)
        return [*qs]

    @classmethod
    def _method_2(cls, playlist):
        qs = TrackFeatures.objects.filter(track__playlist=playlist)
        return [*qs]

    @classmethod
    def _method_3(cls, playlist):
        q = (
            "SELECT music_trackfeatures.* "
            "FROM music_track_playlist "
            "INNER JOIN music_track ON (music_track_playlist.track_id = music_track.id)"
            f" AND music_track_playlist.userplaylist_id = {playlist.id} "
            "INNER JOIN music_trackfeatures ON "
            "(music_track.id = music_trackfeatures.track_id) "
        )
        qs = TrackFeatures.objects.raw(q)
        return [*qs]

    @skipIf(skip_long_tests, "Skipping long test")
    def test_method_1(self):
        playlist_ids = random.choices(range(number_playlists), k=number_runs)
        playlists = [UserPlaylist.objects.get(pk=id) for id in playlist_ids]
        start = time.time()
        for playlist in playlists:
            self._method_1(playlist)
        end = time.time()
        print("time taken for method 1:", end - start)

    @skipIf(skip_long_tests, "Skipping long test")
    def test_method_2(self):
        playlist_ids = random.choices(range(number_playlists), k=number_runs)
        playlists = [UserPlaylist.objects.get(pk=id) for id in playlist_ids]
        start = time.time()
        for playlist in playlists:
            self._method_2(playlist)
        end = time.time()
        print("time taken for method 2:", end - start)

    @skipIf(skip_long_tests, "Skipping long test")
    def test_method_3(self):
        playlist_ids = random.choices(range(number_playlists), k=number_runs)
        playlists = [UserPlaylist.objects.get(pk=id) for id in playlist_ids]
        start = time.time()
        for playlist in playlists:
            self._method_3(playlist)
        end = time.time()
        print("time taken for method 3:", end - start)

    @skipIf(skip_long_tests, "Skipping long test")
    def test_methods_are_equal(self):
        playlist_ids = random.choices(range(number_playlists), k=number_runs)
        playlists = [UserPlaylist.objects.get(pk=id) for id in playlist_ids]
        for playlist in playlists:
            # method 1
            q1 = self._method_1(playlist)

            # method 2
            q2 = self._method_2(playlist)

            # method 3
            q3 = self._method_3(playlist)

            # test lengths are equal
            l1 = len(q1)
            l2 = len(q2)
            l3 = len(q3)

            self.assertEqual(l1, l2)
            self.assertEqual(l1, l3)

            q1.sort(key=lambda t: t["track_features__id"])
            q2.sort(key=lambda t: t.id)
            q3.sort(key=lambda t: t.id)

            for tf1, tf2, tf3 in zip(q1, q2, q3):
                self.assertEqual(tf1["track_features__id"], tf2.id)
                self.assertEqual(tf1["track_features__id"], tf3.id)
