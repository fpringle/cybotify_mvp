from django.urls import path

from stats.views import playlist_detail

from . import views

urlpatterns = [
    path("playlists/", views.playlists, name="playlists"),
    path("playlists/<int:playlist_id>", playlist_detail, name="playlist-detail"),
]
