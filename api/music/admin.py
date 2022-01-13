from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from .models import Track, TrackFeatures, UserPlaylist


class TrackFeaturesInlineAdmin(admin.StackedInline):
    model = TrackFeatures

    def has_change_permission(self, req, obj=None):
        return False


class TrackFeaturesAdmin(admin.ModelAdmin):
    model = TrackFeatures

    def has_change_permission(self, req, obj=None):
        return False


class TrackAdmin(admin.ModelAdmin):
    model = Track
    fieldsets = [
        ("Track info", {"fields": ["spotify_id", "name", "artist_list", "album"]}),
    ]
    search_fields = ("spotify_id", "name", "artists", "album")
    inlines = [TrackFeaturesInlineAdmin]

    @admin.display(description="Artists")
    def artist_list(self, obj):
        return ", ".join(obj.artist_list)

    def has_change_permission(self, req, obj=None):
        return False


class TrackInlineAdmin(admin.TabularInline):
    model = Track


class UserPlaylistAdmin(admin.ModelAdmin):
    model = UserPlaylist
    readonly_fields = fields = (
        "spotify_id",
        "snapshot_id",
        "name",
        "_users",
        "last_updated",
        "owner",
        "tracks",
    )
    search_fields = ("spotify_id", "snapshot_id", "name", "owner")
    actions = ["update_playlists"]

    @admin.action(description="Update selected playlists' information")
    def update_playlists(self, request, queryset):
        for playlist in queryset:
            playlist.check_update(False)

    def tracks(self, obj):
        list_items = format_html_join(
            "\n",
            '<li><a href="{}">{}</a></li>',
            (
                (
                    reverse("admin:music_track_change", args=(track.pk,)),
                    track.name,
                )
                for track in sorted(obj.track_set.all(), key=lambda tr: tr.name)
            ),
        )
        return format_html("<ul>{}</ul>", list_items)

    @admin.display(description="Users")
    def _users(self, obj):
        list_items = format_html_join(
            "\n",
            '<li><a href="{}">{}</a></li>',
            (
                (
                    reverse("admin:accounts_spotifyuser_change", args=(user.pk,)),
                    user.spotify_id,
                )
                for user in obj.users.all()
            ),
        )
        return format_html("<ul>{}</ul>", list_items)


admin.site.register(Track, TrackAdmin)
admin.site.register(UserPlaylist, UserPlaylistAdmin)
admin.site.register(TrackFeatures, TrackFeaturesAdmin)
