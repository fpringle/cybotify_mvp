from django.urls import include, path

from . import views

urlpatterns = [
    path('user/new/', views.new_user, name='new_user'),
    path('user/new/callback/', views.handle_spotify_auth_response, name="new_user_callback"),
    path('stats/', include('server.stats.urls')),
]
