"""
Custom throttle classes for rate limiting
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Rate throttle for authentication endpoints
    """
    scope = 'auth'
    rate = '10/minute'  # 10 requests per minute for auth endpoints


class BurstRateThrottle(UserRateThrottle):
    """
    Burst rate throttle for authenticated users
    """
    scope = 'burst'
    rate = '60/minute'  # 60 requests per minute burst


class SustainedRateThrottle(UserRateThrottle):
    """
    Sustained rate throttle for authenticated users
    """
    scope = 'sustained'
    rate = '1000/hour'  # 1000 requests per hour sustained