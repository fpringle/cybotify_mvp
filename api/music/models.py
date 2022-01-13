from django.db import models
from django.utils.translation import gettext_lazy as _

from api.accounts import SpotifyManager


class UserPlaylistManager(models.Manager):
    def create_or_update(self, playlist_data, user, position):
        spotify_id = playlist_data["id"]
        name = playlist_data["name"]
        status = SpotifyManager.get_playlist_status(playlist_data)
        owner = playlist_data["owner"]["id"]

        playlist, created = self.update_or_create(
            spotify_id=spotify_id,
            defaults={
                "name": name,
                "status": status,
                "owner": owner,
            },
        )

        SpotifyUserPlaylistRelationship.objects.update_or_create(
            user=user, playlist=playlist, defaults={"playlist_position": position}
        )


class UserPlaylist(models.Model):
    # make spotify_id unique
    spotify_id = models.CharField(max_length=256, unique=True)
    snapshot_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    users = models.ManyToManyField(
        "accounts.SpotifyUser", through="SpotifyUserPlaylistRelationship"
    )
    owner = models.CharField(max_length=256)
    last_updated = models.DateTimeField(auto_now=True)
    objects = UserPlaylistManager()

    class Status(models.TextChoices):
        PRIVATE = "PR", _("Private")
        PUBLIC = "PU", _("Public")
        COLLABORATIVE = "CO", _("Collaborative")

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
    )

    def is_user_allowed(self, user):
        if self.status == "PU":
            # anyone can view a public playlist
            return True
        else:
            # private playlists can only be seen by their owner,
            # collab playlists can be seen by any collaborators
            return self.users.filter(user__id=user.id).exists()

    def get_client(self):
        if self.status == "PU":
            return SpotifyManager.app_client
        else:
            if not self.users.all().exists():
                raise Exception(
                    "We don't have credentials for any of the "
                    f"collaborators on playlist {self.pk}"
                )
            user = self.users.first().user
            user.credentials.check_expired()
            return SpotifyManager.user_client(user.credentials.access_token)

    def get_latest_snapshot(self):
        sp = self.get_client()
        return sp.playlist(self.spotify_id, fields="snapshot_id")["snapshot_id"]

    def needs_update(self):
        current = self.get_latest_snapshot()
        return (current != self.snapshot_id, current)

    def update_tracks(self, get_features=True):
        sp = self.get_client()
        tracks = SpotifyManager.get_playlist_tracks(sp, self.spotify_id)
        for position, track_data in enumerate(tracks, 0):
            artists = " =|AND|= ".join(
                artist["name"] for artist in track_data["artists"]
            )
            track, created = Track.objects.get_or_create(
                spotify_id=track_data["id"],
                defaults={
                    "name": track_data["name"],
                    "artists": artists,
                    "album": track_data["album"]["name"],
                },
            )

            PlaylistTrackRelationship.objects.update_or_create(
                playlist=self, track=track, defaults={"track_position": position}
            )

        self.save()

        track_ids = [tr["id"] for tr in tracks if "id" in tr]
        to_remove = self.track_set.filter(~models.Q(spotify_id__in=track_ids))
        self.track_set.remove(*to_remove)

        if get_features:
            self.update_track_features()

    def check_update(self, get_features=True):
        needs_update, current = self.needs_update()
        if not needs_update:
            print("  Already up to date")
            return

        # TODO update the info about the playlist itself
        #  e.g. name, status, owner
        print(
            f"Playlist {self.name} - checking for updates "
            f"(DB snapshot ID {self.snapshot_id})"
        )
        print(f"  Spotify latest snapshot id is {current}, updating")

        self.update_tracks(get_features)
        self.snapshot_id = current

    def update_track_features(self):
        missing = self.track_set.filter(track_features=None, features_unavailable=False)
        track_ids = [track.spotify_id for track in missing]
        features = SpotifyManager.get_track_features(track_ids)
        for track, features_data in zip(missing, features):
            if not features_data:
                track.features_unavailable = True
                track.save()
                continue
            track.track_features = TrackFeatures.objects.create(
                track=track,
                acousticness=features_data["acousticness"],
                danceability=features_data["danceability"],
                energy=features_data["energy"],
                instrumentalness=features_data["instrumentalness"],
                key=features_data["key"],
                liveness=features_data["liveness"],
                loudness=features_data["loudness"],
                mode=features_data["mode"],
                speechiness=features_data["speechiness"],
                tempo=features_data["tempo"],
                time_signature=features_data["time_signature"],
                valence=features_data["valence"],
            )
            track.save()
        self.save()

    def __str__(self):
        return (
            f"(name={self.name}, status={self.status}, " f"spotifyID={self.spotify_id})"
        )


class SpotifyUserPlaylistRelationship(models.Model):
    user = models.ForeignKey("accounts.SpotifyUser", on_delete=models.CASCADE)
    playlist = models.ForeignKey(UserPlaylist, on_delete=models.CASCADE)
    playlist_position = models.IntegerField()

    class Meta:
        unique_together = ("user", "playlist")


class Track(models.Model):
    spotify_id = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    artists = models.CharField(max_length=256)
    album = models.CharField(max_length=256)
    playlist = models.ManyToManyField(UserPlaylist, through="PlaylistTrackRelationship")
    features_unavailable = models.BooleanField(default=False)

    @property
    def artist_list(self):
        return self.artists.split(" =|AND|= ")

    @property
    def artists_comma_separated(self):
        return ", ".join(self.artist_list)

    def get_features(self):
        # note: this is a VERY slow way of getting track features!
        # if possible, user UserPlaylist.update_track_features
        if hasattr(self, "track_features"):
            return
        if self.features_unavailable:
            return
        print(f"getting features for track '{self.name}'")
        track_features_data = SpotifyManager.get_track_features([self.spotify_id])[0]
        self.track_features = TrackFeatures(
            track=self,
            acousticness=track_features_data["acousticness"],
            danceability=track_features_data["danceability"],
            energy=track_features_data["energy"],
            instrumentalness=track_features_data["instrumentalness"],
            key=track_features_data["key"],
            liveness=track_features_data["liveness"],
            loudness=track_features_data["loudness"],
            mode=track_features_data["mode"],
            speechiness=track_features_data["speechiness"],
            tempo=track_features_data["tempo"],
            time_signature=track_features_data["time_signature"],
            valence=track_features_data["valence"],
        )
        self.track_features.save()
        self.save()

    def __str__(self):
        return (
            f"(name={self.name}, artists={self.artists}, spotifyID={self.spotify_id})"
        )


class PlaylistTrackRelationship(models.Model):
    playlist = models.ForeignKey(UserPlaylist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    track_position = models.IntegerField()

    class Meta:
        unique_together = ("playlist", "track")


class TrackFeatures(models.Model):
    track = models.OneToOneField(
        Track, on_delete=models.CASCADE, related_name="track_features"
    )

    class Mode(models.IntegerChoices):
        MAJOR = 1
        MINOR = 0

    acousticness = models.FloatField()
    danceability = models.FloatField()
    energy = models.FloatField()
    instrumentalness = models.FloatField()
    key = models.SmallIntegerField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.IntegerField(choices=Mode.choices)
    speechiness = models.FloatField()
    tempo = models.FloatField()
    time_signature = models.SmallIntegerField()
    valence = models.FloatField()

    def __str__(self):
        return self.track.__str__()
