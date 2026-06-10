import logging

from django.core.exceptions import (
    PermissionDenied,
    ValidationError as DjangoValidationError,
)
from django.http import Http404

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def momaid_exception_handler(exc, context):

    if isinstance(exc, Http404):
        exc = _drf_exc("Not found.", status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, PermissionDenied):
        exc = _drf_exc("Permission denied.", status.HTTP_403_FORBIDDEN)
    elif isinstance(exc, DjangoValidationError):
        exc = _drf_exc(exc.message, status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)

    if response is None:
        logger.error("Unhandled exception reached DRF handler", exc_info=exc)
        return Response(
            _error_body("An unexpected error occurred.", None),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    errors = None
    message = "An error occurred."

    if isinstance(response.data, dict):

        if "detail" in response.data:
            message = str(response.data["detail"])
        else:

            message = "Validation failed."
            errors = response.data
    elif isinstance(response.data, list):
        message = str(response.data[0]) if response.data else message
    elif isinstance(response.data, str):
        message = response.data

    response.data = _error_body(message, errors)
    return response


class MomAidException(APIException):
    """Base for all Momaid domain exceptions."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred."


class ConflictError(MomAidException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Resource already exists."


class ServiceUnavailable(MomAidException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service temporarily unavailable."


def _drf_exc(detail: str, status_code: int) -> APIException:
    exc = APIException(detail)
    exc.status_code = status_code
    return exc


def _error_body(message: str, errors) -> dict:
    return {
        "status": "error",
        "message": message,
        "errors": errors,
    }
