"""Throttling for authentication endpoints."""

from rest_framework.throttling import SimpleRateThrottle


class AuthThrottle(SimpleRateThrottle):
    """Limit OTP and verify attempts."""

    scope = "auth"

    def get_cache_key(self, request, view) -> str | None:
        ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
