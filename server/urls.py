from django.urls import path

from . import views

urlpatterns = [
    path('user/new/', views.new_user, name='new user'),
    path('user/new/callback', views.handle_spotify_auth_response),
]
