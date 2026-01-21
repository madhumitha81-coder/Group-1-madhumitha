from django.conf import settings
from django.http import JsonResponse

class VerifyFrontendTokenMiddleware:
    """
    Middleware to verify frontend token on /api/ routes.
    Skips verification in DEBUG mode for local dev.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip OPTIONS requests
        if request.method == "OPTIONS":
            return self.get_response(request)

        # Only check API routes
        if request.path.startswith("/api/"):
            # Only enforce token in production
            if not settings.DEBUG:
                token = request.headers.get("X-Frontend-Token")
                if token != settings.FRONTEND_ACCESS_TOKEN:
                    return JsonResponse({"error": "Unauthorized"}, status=401)

        return self.get_response(request)
