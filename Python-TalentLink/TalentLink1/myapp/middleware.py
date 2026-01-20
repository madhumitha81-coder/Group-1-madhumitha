from django.conf import settings
from django.http import JsonResponse

class VerifyFrontendTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("X-Frontend-Token")
        # Check if token matches
        if token != settings.FRONTEND_ACCESS_TOKEN:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        return self.get_response(request)
