from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path("new/", views.new_user, name="new_user"),
    path("new/callback/", views.handle_spotify_auth_response, name="new_user_callback"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html")),
    path("logout/", views.logout, name="logout"),
    path("new/create_password/", views.create_password, name="create-password"),
    path("", include("django.contrib.auth.urls")),
]
