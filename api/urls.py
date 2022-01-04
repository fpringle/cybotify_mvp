from django.urls import include, path

urlpatterns = [
    path("accounts/", include("api.accounts.urls")),
    path("music/", include("api.music.urls")),
    path("stats/", include("api.stats.urls")),
]
