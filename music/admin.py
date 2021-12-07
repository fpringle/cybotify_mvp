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
        def get_li(track):
            list_items = format_html_join(
                "\n",
                '<li><a href="{}">{}</a></li>',
                (
                    (
                        reverse("admin:music_track_change", args=(track.pk,)),
                        track.name,
                    )
                    for track in obj.track_set.all()
                ),
            )
            return format_html("<ul>{}</ul>", list_items)


class UserPlaylistInlineAdmin(admin.TabularInline):
    model = UserPlaylist
    extra = 0
    fields = ("name", "link", "spotify_id", "snapshot_id", "last_updated")
    readonly_fields = ("link", "last_updated")

    @admin.display(description="Link")
    def link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:music_userplaylist_change", args=(obj.pk,)),
            obj.name,
        )


admin.site.register(Track, TrackAdmin)
admin.site.register(UserPlaylist, UserPlaylistAdmin)
admin.site.register(TrackFeatures, TrackFeaturesAdmin)
