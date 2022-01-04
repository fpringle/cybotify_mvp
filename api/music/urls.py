from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

playlist_list = views.PlaylistViewSet.as_view(
    {
        "get": "list",
    }
)
playlist_detail = views.PlaylistViewSet.as_view(
    {
        "get": "retrieve",
    }
)
playlist_features = views.PlaylistFeaturesViewSet.as_view(
    {
        "get": "retrieve",
    }
)
track_detail = views.TrackViewSet.as_view(
    {
        "get": "retrieve",
    }
)
track_features = views.TrackFeaturesViewSet.as_view(
    {
        "get": "retrieve",
    }
)


urlpatterns = [
    path("playlists/", playlist_list, name="playlists"),
    path("playlists/<int:pk>", playlist_detail, name="playlist-detail"),
    path("playlists/<int:pk>/features/", playlist_features, name="playlist-features"),
    path("tracks/<int:pk>/", track_detail, name="track-detail"),
    path("tracks/<int:pk>/features/", track_features, name="track-features"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
