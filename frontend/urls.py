# music
from django.contrib.auth import views as auth_views
from django.urls import include, path

from api.accounts.views import logout

from . import views

app_name = "frontend"
urlpatterns = [
    path("", views.index, name="index"),
    path("playlists/", views.playlists, name="playlists"),
    path("playlists/<int:playlist_id>", views.playlist_detail, name="playlist-detail"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html")),
    path("create_password/", views.create_password, name="create-password"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("logout/", logout, name="logout"),
    path("", include("django.contrib.auth.urls")),
]
