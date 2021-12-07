import logging

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import (
    RegistrationState,
    SpotifyUser,
    SpotifyUserCredentials,
)

from music.admin import UserPlaylistInlineAdmin

logger = logging.getLogger("admin")


class SpotifyUserInlineAdmin(admin.StackedInline):
    model = SpotifyUser
    fields = [
        "user",
        "user_link",
    ]
    list_display = ["user_link"]
    readonly_fields = ("user_link",)

    def user_link(self, obj):
        if not obj.user:
            return "No spotify user is associated with this account."

        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:accounts_spotifyuser_change", args=(obj.pk,)),
                obj.user.spotifyuser.spotify_id,
            )
        )

    user_link.short_description = "Link"


class SpotifyUserAdmin(admin.ModelAdmin):
    model = SpotifyUser
    inlines = [UserPlaylistInlineAdmin]


class SpotifyUserCredentialsAdmin(admin.StackedInline):
    model = SpotifyUserCredentials
    fields = ["access_token", "refresh_token", "has_expired", "expires_at"]
    readonly_fields = ["has_expired", "expires_at"]

    def has_expired(self, obj):
        return obj.has_expired


class UserAdmin(BaseUserAdmin):
    model = User
    inlines = [SpotifyUserInlineAdmin, SpotifyUserCredentialsAdmin]


class RegistrationStateAdmin(admin.ModelAdmin):
    model = RegistrationState


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(SpotifyUser, SpotifyUserAdmin)
admin.site.register(RegistrationState, RegistrationStateAdmin)
