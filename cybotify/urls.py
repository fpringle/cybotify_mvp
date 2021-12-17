from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("", index, name="index"),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
]
