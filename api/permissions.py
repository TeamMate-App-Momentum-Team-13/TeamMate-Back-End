from rest_framework import permissions


# Allows only owner of object to access object
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.host_id == request.user


# Allows only owner of game session object to edit object
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.host == request.user

# This permission comes from this great stack overflow posting
# https://stackoverflow.com/questions/19313314/django-rest-framework-viewset-per-action-permissions
class GuestPermission(permissions.BasePermission):
                                                                                                
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated
        elif view.action == 'create':
            return request.user.is_authenticated
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False
                                                                                                
    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.user.is_authenticated:
            return False

        if view.action == 'retrieve':
            return obj.user == request.user or request.user.is_staff
        elif view.action in ['update', 'partial_update']:
            return obj.game_session.host == request.user or request.user.is_staff
        elif view.action == 'destroy':
            return obj.user == request.user or request.user.is_staff
        else:
            return False
