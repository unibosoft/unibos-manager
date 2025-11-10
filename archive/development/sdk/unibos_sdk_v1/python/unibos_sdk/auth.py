"""
UNIBOS Authentication Helpers

Authentication and authorization utilities for modules.
"""

from functools import wraps
from typing import Optional
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

User = get_user_model()


class UnibosAuth:
    """Authentication helpers for UNIBOS modules"""

    @staticmethod
    def get_current_user(request):
        """
        Get current authenticated user from request

        Args:
            request: Django request object

        Returns:
            User object if authenticated, None otherwise
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
        return None

    @staticmethod
    def check_permission(user, permission: str) -> bool:
        """
        Check if user has a specific permission

        Args:
            user: User object
            permission: Permission string (e.g., 'birlikteyiz.view_earthquake')

        Returns:
            True if user has permission, False otherwise
        """
        if not user or not user.is_authenticated:
            return False

        return user.has_perm(permission)

    @staticmethod
    def check_any_permission(user, permissions: list) -> bool:
        """
        Check if user has any of the specified permissions

        Args:
            user: User object
            permissions: List of permission strings

        Returns:
            True if user has at least one permission, False otherwise
        """
        if not user or not user.is_authenticated:
            return False

        return any(user.has_perm(perm) for perm in permissions)

    @staticmethod
    def check_all_permissions(user, permissions: list) -> bool:
        """
        Check if user has all of the specified permissions

        Args:
            user: User object
            permissions: List of permission strings

        Returns:
            True if user has all permissions, False otherwise
        """
        if not user or not user.is_authenticated:
            return False

        return all(user.has_perm(perm) for perm in permissions)

    @staticmethod
    def require_authentication(func):
        """
        Decorator to require authentication

        Usage:
            @UnibosAuth.require_authentication
            def my_view(request):
                # User is guaranteed to be authenticated
                pass
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise NotAuthenticated('Authentication required')
            return func(request, *args, **kwargs)
        return wrapper

    @staticmethod
    def require_permission(permission: str):
        """
        Decorator to require specific permission

        Usage:
            @UnibosAuth.require_permission('birlikteyiz.view_earthquake')
            def my_view(request):
                # User is guaranteed to have permission
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    raise NotAuthenticated('Authentication required')

                if not request.user.has_perm(permission):
                    raise PermissionDenied(
                        f'Permission required: {permission}'
                    )

                return func(request, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def require_any_permission(*permissions):
        """
        Decorator to require any of the specified permissions

        Usage:
            @UnibosAuth.require_any_permission('birlikteyiz.view', 'birlikteyiz.edit')
            def my_view(request):
                # User has at least one of the permissions
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    raise NotAuthenticated('Authentication required')

                if not any(request.user.has_perm(p) for p in permissions):
                    raise PermissionDenied(
                        f'One of these permissions required: {", ".join(permissions)}'
                    )

                return func(request, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def require_all_permissions(*permissions):
        """
        Decorator to require all of the specified permissions

        Usage:
            @UnibosAuth.require_all_permissions('birlikteyiz.view', 'birlikteyiz.edit')
            def my_view(request):
                # User has all of the permissions
                pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    raise NotAuthenticated('Authentication required')

                if not all(request.user.has_perm(p) for p in permissions):
                    raise PermissionDenied(
                        f'All of these permissions required: {", ".join(permissions)}'
                    )

                return func(request, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def is_superuser(user) -> bool:
        """
        Check if user is superuser

        Args:
            user: User object

        Returns:
            True if user is superuser, False otherwise
        """
        if not user or not user.is_authenticated:
            return False

        return user.is_superuser

    @staticmethod
    def require_superuser(func):
        """
        Decorator to require superuser status

        Usage:
            @UnibosAuth.require_superuser
            def admin_view(request):
                # Only superusers can access
                pass
        """
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise NotAuthenticated('Authentication required')

            if not request.user.is_superuser:
                raise PermissionDenied('Superuser access required')

            return func(request, *args, **kwargs)
        return wrapper
