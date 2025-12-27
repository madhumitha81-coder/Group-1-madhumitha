from rest_framework import permissions


from rest_framework.permissions import BasePermission

class IsProjectOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Safe methods allowed for anyone. Modification allowed only if the user owns the object.
    Ownership is inferred for objects that have client, freelancer, sender fields.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # object types with client/freelancer/sender
        if hasattr(obj, 'client'):
            return obj.client.user == request.user
        if hasattr(obj, 'freelancer'):
            return obj.freelancer.user == request.user
        if hasattr(obj, 'sender'):
            return obj.sender.user == request.user
        return False

class IsClientOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user
