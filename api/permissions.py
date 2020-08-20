from rest_framework import permissions

from api.models import UserConfig


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.config.role == UserConfig.USER_ROLE_ADMIN
        except:
            return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.config.role == UserConfig.USER_ROLE_REALTOR or request.user.config.role == UserConfig.USER_ROLE_ADMIN

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return request.user.config.role == UserConfig.USER_ROLE_ADMIN \
            or (request.user.config.role == UserConfig.USER_ROLE_REALTOR and obj.realtor == request.user)
