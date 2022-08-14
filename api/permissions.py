from rest_framework import permissions


# allows only owner of object to access object
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.host_id == request.user


# allows only owner of object to edit object
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.host_id == request.user