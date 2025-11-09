"""
Custom exception handler for UNIBOS API
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that logs errors and provides consistent error responses
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Log the exception
    logger.error(f"API Exception: {exc}", exc_info=True, extra={
        'request': context.get('request'),
        'view': context.get('view'),
    })

    # Now add the HTTP status code to the response.
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data

    return response