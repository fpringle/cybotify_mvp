from rest_framework import permissions


class HasSpotifyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            hasattr(request.user, "spotifyuser")
            and request.user.spotifyuser is not None
        )


class HasPlaylistAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.username == "admin":
            return False
        return obj.is_user_allowed(request.user.spotifyuser)
