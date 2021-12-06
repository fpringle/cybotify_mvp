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
    UserPlaylist,
    Track,
    TrackFeatures,
)

logger = logging.getLogger("admin")


class TrackFeaturesInlineAdmin(admin.StackedInline):
    model = TrackFeatures

    def has_change_permission(self, req, obj=None):
        return False

class TrackFeaturesAdmin(admin.ModelAdmin):
    model = TrackFeatures

class TrackAdmin(admin.ModelAdmin):
    model = Track
    fieldsets = [
        ("Track info", {"fields": ["spotify_id", "name", "artist_list", "album"]}),
    ]
    inlines = [TrackFeaturesInlineAdmin]

    @admin.display(description="Artists")
    def artist_list(self, obj):
        return ", ".join(obj.artist_list)

    def has_change_permission(self, req, obj=None):
        return False


class TrackInlineAdmin(admin.TabularInline):
    model = Track


class UserPlaylistInlineAdmin(admin.TabularInline):
    model = UserPlaylist
    extra = 0
    fields = ("name", "link", "spotify_id", "snapshot_id", "last_updated")
    readonly_fields = ("link", "last_updated")

    @admin.display(description="Link")
    def link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:server_userplaylist_change", args=(obj.pk,)), obj.name
            )
        )


class UserPlaylistAdmin(admin.ModelAdmin):
    model = UserPlaylist
    fields = (
        "spotify_id",
        "snapshot_id",
        "name",
        "user",
        "tracks",
        "last_updated",
    )
    readonly_fields = ("tracks", "last_updated")

    def tracks(self, obj):
        def get_link(track):
            return '<a href="{}">{}</a>'.format(
                reverse("admin:server_track_change", args=(track.pk,)), track.name
            )

        def get_li(track):
            return "<li>" + get_link(track) + "</li>"

        return mark_safe("<ul>" + "".join(map(get_li, obj.track_set.all())) + "</ul>")


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
                reverse("admin:server_spotifyuser_change", args=(obj.pk,)),
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
admin.site.register(Track, TrackAdmin)
admin.site.register(SpotifyUser, SpotifyUserAdmin)
admin.site.register(UserPlaylist, UserPlaylistAdmin)
admin.site.register(RegistrationState, RegistrationStateAdmin)
admin.site.register(TrackFeatures, TrackFeaturesAdmin)
