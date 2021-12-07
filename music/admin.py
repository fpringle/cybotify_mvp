from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

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
        def get_link(track):
            return '<a href="{}">{}</a>'.format(
                reverse("admin:music_track_change", args=(track.pk,)), track.name
            )

        def get_li(track):
            return "<li>" + get_link(track) + "</li>"

        return mark_safe("<ul>" + "".join(map(get_li, obj.track_set.all())) + "</ul>")


class UserPlaylistInlineAdmin(admin.TabularInline):
    model = UserPlaylist
    extra = 0
    fields = ("name", "link", "spotify_id", "snapshot_id", "last_updated")
    readonly_fields = ("link", "last_updated")

    @admin.display(description="Link")
    def link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:music_userplaylist_change", args=(obj.pk,)), obj.name
            )
        )


admin.site.register(Track, TrackAdmin)
admin.site.register(UserPlaylist, UserPlaylistAdmin)
admin.site.register(TrackFeatures, TrackFeaturesAdmin)
