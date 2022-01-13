import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import RegistrationState, SpotifyUser, SpotifyUserCredentials

logger = logging.getLogger("admin")


class SpotifyUserInlineAdmin(admin.StackedInline):
    model = SpotifyUser
    readonly_fields = fields = [
        "user",
        "user_link",
    ]
    list_display = ["user_link"]

    def user_link(self, obj):
        if not obj.user:
            return "No spotify user is associated with this account."

        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:accounts_spotifyuser_change", args=(obj.pk,)),
            obj.user.spotifyuser.spotify_id,
        )

    user_link.short_description = "Link"


class SpotifyUserAdmin(admin.ModelAdmin):
    model = SpotifyUser
    readonly_fields = fields = ("user", "spotify_id", "_playlists")
    search_fields = ("user__username", "spotify_id")

    @admin.display(description="Playlists")
    def _playlists(self, obj):
        list_items = format_html_join(
            "\n",
            '<li><a href="{}">{}</a></li>',
            (
                (
                    reverse("admin:music_userplaylist_change", args=(playlist.pk,)),
                    playlist.name,
                )
                for playlist in sorted(
                    obj.userplaylist_set.all(), key=lambda pl: pl.name
                )
            ),
        )
        return format_html("<ul>{}</ul>", list_items)


class SpotifyUserCredentialsAdmin(admin.StackedInline):
    model = SpotifyUserCredentials
    readonly_fields = fields = [
        "access_token",
        "refresh_token",
        "has_expired",
        "expires_at",
    ]

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
