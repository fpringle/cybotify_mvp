from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("", index, name="index"),
    path("accounts/", include("accounts.urls")),
    path("music/", include("music.urls")),
    path("stats/", include("stats.urls")),
    path("admin/", admin.site.urls),
]
