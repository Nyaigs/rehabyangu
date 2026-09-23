"""Public API error responses.

Never serialise exception strings from unexpected failures: they can contain
database details, paths, or object representations.  Expected DRF errors are
reduced to a stable code/message pair as well.
"""
import logging

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception('Unhandled API exception', exc_info=exc)
        return Response(
            {'error': {'code': 'internal_error', 'message': 'An unexpected error occurred.'}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    from authorization.exceptions import FeatureNotInPlan
    if isinstance(exc, FeatureNotInPlan):
        response.data = exc.detail
        return response

    code = getattr(exc, 'default_code', 'api_error')
    message = 'Request could not be completed.'
    if isinstance(exc, ValidationError):
        code = 'validation_error'
        message = 'One or more submitted values are invalid.'
    elif isinstance(exc, APIException):
        # Default detail strings are framework-controlled and do not expose
        # model or database internals.
        detail = getattr(exc, 'default_detail', None)
        if detail:
            message = str(detail)
    response.data = {'error': {'code': str(code), 'message': message}}
    return response
