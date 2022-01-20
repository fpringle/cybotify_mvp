from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Track, UserPlaylist
from .permissions import HasPlaylistAccess, HasSpotifyUser
from .serializers import (
    PlaylistDetailSerializer,
    PlaylistFeaturesSerializer,
    PlaylistSerializer,
    TrackSerializer,
    TrackWithFeaturesSerializer,
)


class PlaylistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserPlaylist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasSpotifyUser,
        HasPlaylistAccess,
    ]

    def list(self, request, format=None):
        su = request.user.spotifyuser
        su.update_playlists()
        ordering = "spotifyuserplaylistrelationship__playlist_position"
        playlists = su.userplaylist_set.all().order_by(ordering)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk, format=None):
        try:
            playlist = UserPlaylist.objects.get(pk=pk)
        except UserPlaylist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        playlist.check_update(False)
        serializer = PlaylistDetailSerializer(playlist)
        return Response(serializer.data)


class PlaylistFeaturesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserPlaylist.objects.all()
    serializer_class = PlaylistFeaturesSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        HasSpotifyUser,
        HasPlaylistAccess,
    ]

    def retrieve(self, request, pk, format=None):
        try:
            playlist = UserPlaylist.objects.get(pk=pk)
        except UserPlaylist.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        playlist.check_update(True)
        serializer = PlaylistFeaturesSerializer(playlist)
        return Response(serializer.data)


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [permissions.IsAuthenticated, HasSpotifyUser]


class TrackFeaturesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackWithFeaturesSerializer
    permission_classes = [permissions.IsAuthenticated, HasSpotifyUser]

    def retrieve(self, request, pk, format=None):
        try:
            track = Track.objects.get(pk=pk)
        except Track.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        track.get_features()
        serializer = TrackWithFeaturesSerializer(track)
        return Response(serializer.data)
