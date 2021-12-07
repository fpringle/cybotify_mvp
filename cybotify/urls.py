from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('accounts.urls')),
    path('', include('music.urls')),
    path('stats/', include('stats.urls')),
    path('admin/', admin.site.urls),
]
