from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "server_error",
                    "message": "Unexpected server error.",
                    "details": {},
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(response.data, dict):
        details = response.data
        message = details.get("detail")
        if isinstance(message, list):
            message = message[0]
        if not message:
            message = "Request failed."
    else:
        details = {"detail": response.data}
        message = "Request failed."

    response.data = {
        "ok": False,
        "error": {
            "code": f"http_{response.status_code}",
            "message": str(message),
            "details": details,
        },
    }
    return response
