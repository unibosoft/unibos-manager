"""
Custom permissions for Currencies module
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            # Check if object is public (for portfolios)
            if hasattr(obj, 'is_public') and obj.is_public:
                return True
            # Otherwise, only owner can read
            if hasattr(obj, 'user'):
                return obj.user == request.user
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsPortfolioOwner(permissions.BasePermission):
    """
    Permission to check if user owns the portfolio
    """
    
    def has_permission(self, request, view):
        # Allow list and create
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if user owns the portfolio
        return obj.user == request.user


class IsAlertOwner(permissions.BasePermission):
    """
    Permission to check if user owns the alert
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow admin write access and read-only for others
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff