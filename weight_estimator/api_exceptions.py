from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    resp = exception_handler(exc, context)
    if resp is None:
        return Response(
            {"detail": "Unexpected server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Normalize DRF error shape
    if isinstance(resp.data, dict) and "detail" not in resp.data:
        return Response({"detail": "Validation error.", "errors": resp.data}, status=resp.status_code)

    return resp

