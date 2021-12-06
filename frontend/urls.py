from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', auth_views.LoginView.as_view(template_name='frontend/login.html')),
    path('logout/', views.logout, name="logout"),
    path('user/new/create_password/', views.create_password, name="create-password"),
    path('register/', views.register, name="register"),
    path('profile/', views.profile, name="profile"),
    path('playlists/', views.playlists, name="playlists"),
    path('playlists/<int:playlist_id>', views.playlist_detail, name="playlist-detail"),

    path('', include('django.contrib.auth.urls')),
]
