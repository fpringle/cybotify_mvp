from django.db import models

from accounts.spotify_client_info import (
    get_spotify_user_client,
    get_all_playlist_tracks,
    get_all_track_features,
    get_spotify_client,
)


class UserPlaylist(models.Model):
    spotify_id = models.CharField(max_length=256)
    snapshot_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    user = models.ForeignKey("SpotifyUser", on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)

    def get_latest_snapshot(self):
        su = self.user.user
        su.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(su.spotifyusercredentials.access_token)
        return sp.playlist(self.spotify_id, fields="snapshot_id")["snapshot_id"]

    def update_tracks(self):
        su = self.user.user
        su.spotifyusercredentials.check_expired()
        sp = get_spotify_user_client(su.spotifyusercredentials.access_token)
        tracks = get_all_playlist_tracks(sp, self.spotify_id)
        for track_data in tracks:
            if Track.objects.filter(spotify_id=track_data["id"]).exists():
                track = Track.objects.get(spotify_id=track_data["id"])
                #track.get_features()
                if not self.track_set.filter(pk=track.pk).exists():
                    self.track_set.add(track)
                continue
            track = Track.objects.create(
                spotify_id=track_data["id"],
                name=track_data["name"],
                artists=" =|AND|= ".join(
                    artist["name"] for artist in track_data["artists"]
                ),
                album=track_data["album"]["name"],
            )
            #track.get_features()
            track.save()
            self.track_set.add(track)

        self.save()
        self.update_track_features()

    def check_update(self):
        current = self.get_latest_snapshot()
        if current == self.snapshot_id:
            print("  Already up to date")
            return
        print(f"Playlist {self.name} - checking for updates (DB snapshot ID {self.snapshot_id})")
        print(f"  Spotify latest snapshot id is {current}, updating")
        self.snapshot_id = current
        #self.save()
        self.update_tracks()

    def update_track_features(self):
        missing = self.track_set.filter(track_features=None)
        track_ids = [track.spotify_id for track in missing]
        sp = get_spotify_client()
        features = get_all_track_features(sp, track_ids)
        for track, features_data in zip(missing, features):
            if not features_data:
                print("No track features available for track", track.name)
                # should mark this somehow
                continue
            print("Got track features for", track.name)
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
        return f"(name={self.name}, user={self.user.user.email}, spotifyID={self.spotify_id})"


class Track(models.Model):
    spotify_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    artists = models.CharField(max_length=256)
    album = models.CharField(max_length=256)
    playlist = models.ManyToManyField(UserPlaylist)

    @property
    def artist_list(self):
        return self.artists.split(" =|AND|= ")

    @property
    def artists_comma_separated(self):
        return ", ".join(self.artist_list)

    def get_features(self):
        ## note: this is a VERY slow way of getting track features!
        ## if possible, user UserPlaylist.update_track_features
        if hasattr(self, "track_features"):
            return
        print(f"getting features for track '{self.name}'")
        sp = get_spotify_client()
        track_features_data = sp.audio_features(self.spotify_id)[0]
        print(track_features_data)
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
