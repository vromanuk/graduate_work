import http
from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse


def token_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer", "").strip()
        if not token:
            return JsonResponse(
                {"message": "Invalid Token"}, status=http.HTTPStatus.UNAUTHORIZED
            )
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return JsonResponse(
                {"message": "Invalid Token"}, status=http.HTTPStatus.BAD_REQUEST
            )
        request.user_id = payload["sub"]
        request.user_email = payload["user_email"]
        return func(request, *args, **kwargs)

    return wrapper
