"""DRF exception handler for consistent API errors."""

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Return errors as ``{"error": "...", "detail": "..."}`` when possible."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, dict):
        detail = response.data
        if "detail" in detail and len(detail) == 1:
            payload = {"error": str(detail["detail"]), "detail": str(detail["detail"])}
        else:
            first_key = next(iter(detail), None)
            if first_key:
                val = detail[first_key]
                msg = val[0] if isinstance(val, list) else val
                payload = {"error": str(msg), "detail": detail}
            else:
                payload = {"error": "Request failed", "detail": detail}
    else:
        payload = {"error": str(response.data), "detail": str(response.data)}

    return Response(payload, status=response.status_code)
