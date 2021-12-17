from django.urls import path

from . import views

urlpatterns = [
    path(
        "playlist/<int:playlist_id>/analysis/",
        views.get_playlist_features,
        name="playlist-analysis",
    ),
]
