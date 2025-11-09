"""
Movies Module Permissions
Custom permission classes for secure access control
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    Custom permission for public content or owner access
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if object has visibility field
        if hasattr(obj, 'visibility'):
            if obj.visibility == 'public':
                return True
        
        # Check if object has is_public field
        if hasattr(obj, 'is_public'):
            if obj.is_public:
                return True
        
        # Owner always has access
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class CanManageCollection(permissions.BasePermission):
    """
    Permission to manage collection items
    """
    
    def has_permission(self, request, view):
        # Authenticated users can create collections
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only collection owner can modify
        return obj.user == request.user