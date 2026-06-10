from rest_framework import status
from rest_framework.response import Response


class SuccessResponseMixin:
    """
    Adds a helper for returning a consistent success envelope
    when you need a custom message alongside data.

    Usage:
        class MyView(SuccessResponseMixin, APIView):
            def post(self, request):
                return self.success(data={"id": 1}, message="Created.", status=201)
    """

    def success(
        self, data=None, message: str = None, status_code: int = status.HTTP_200_OK
    ):
        return Response(
            {"status": "success", "message": message, "data": data},
            status=status_code,
        )
