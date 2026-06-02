from django.conf import settings


class SecurityHeadersMiddleware:
    """Add lightweight security headers without taking a dependency on CSP libs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Referrer-Policy', settings.SECURE_REFERRER_POLICY)
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.setdefault('Content-Security-Policy', settings.CONTENT_SECURITY_POLICY)
        response.setdefault('X-Permitted-Cross-Domain-Policies', 'none')
        return response
