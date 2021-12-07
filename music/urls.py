from django.urls import include, path

from . import views
from stats.views import playlist_detail

urlpatterns = [
    path("playlists/", views.playlists, name="playlists"),
    path("playlists/<int:playlist_id>", playlist_detail, name="playlist-detail"),
]
