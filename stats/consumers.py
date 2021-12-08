from channels.generic.websocket import JsonWebsocketConsumer

from stats.views import get_playlist_average_features


class PlaylistDetailConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        playlist_id = self.scope["url_route"]["kwargs"].get("playlist_id")
        if not playlist_id:
            print("REJECT - no playlist id")
            self.close()
            return
        self.playlist_id = int(playlist_id)

        if not self.user.is_authenticated:
            print("REJECT - user not authenticated")
            self.close()
            return
        if not (hasattr(self.user, "spotifyuser") and self.user.spotifyuser):
            print("REJECT - user not assocaited with a spotify user")
            self.close()
            return

        self.spotify_user = self.user.spotifyuser
        playlist_set = self.spotify_user.userplaylist_set.values_list("id")
        if (self.playlist_id,) not in playlist_set:
            print("REJECT - playlist doesn't belong to user")
            print(f"playlist id: {self.playlist_id}")
            print("user playlist set:", playlist_set)
            self.close()
            return

        self.playlist = self.spotify_user.userplaylist_set.get(pk=self.playlist_id)
        self.accept()

        data = {"name": self.playlist.name}
        self.send_json(data)

        self.playlist.check_update(get_features=False)
        track_data = [
            {"name": track.name, "artists": track.artists_comma_separated}
            for track in self.playlist.track_set.all()
        ]
        data["tracks"] = track_data
        self.send_json(data)

        self.playlist.update_track_features()

        features = get_playlist_average_features(self.playlist)
        data["features"] = features["features"]
        self.send_json(data, close=True)
