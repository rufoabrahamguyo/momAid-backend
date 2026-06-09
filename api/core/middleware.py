import logging
import datetime

from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from redis.exceptions import ResponseError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        user = getattr(request, "user", None)
        user_email = user.email if user and user.is_authenticated else "anonymous"

  
        if (
            isinstance(exception, ResponseError)
            and "max daily request limit exceeded" in str(exception).lower()
        ):
            self._alert_discord({
                "alert": "REDIS QUOTA EXHAUSTED",
                "path": request.path,
                "user": user_email,
            })
            return JsonResponse(
                {
                    "status": "maintenance",
                    "message": "Server temporarily under maintenance. Please try again shortly.",
                    "estimated_back": (
                        timezone.now() + datetime.timedelta(minutes=45)
                    ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                status=503,
            )

        logger.exception(
            "Unhandled exception",
            extra={"path": request.path, "user": user_email},
        )
        self._alert_discord({
            "error": str(exception),
            "path": request.path,
            "user": user_email,
        })
        return None 

    @staticmethod
    def _alert_discord(payload: dict):
        try:
            from mumaid.utils.discord import send_error_to_discord
            send_error_to_discord(payload)
        except Exception:
            logger.warning("Discord alert failed", exc_info=True)





_EXEMPT_PREFIXES = ("/admin/", "/static/", "/media/", "/api/docs/", "/api/schema/")

_PATH_TIERS = [
    ("login",       "login_limit"),
    ("register",    "login_limit"),
    ("resend-otp",  "otp_limit"),
    ("verify",      "otp_limit"),
    ("profile/image", "upload_limit"),
]

_PERIOD_SECONDS = {"minute": 60, "min": 60, "hour": 3600, "day": 86400}


class GlobalRateLimiter:


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if any(path.startswith(p) for p in _EXEMPT_PREFIXES):
            return self.get_response(request)

        tier = self._resolve_tier(request, path)
        limit, window = self._parse_rate(tier)
        identifier = self._identifier(request)

        cache_key = f"rl:{tier}:{identifier}"
        cache.get_or_set(cache_key, 0, window)
        count = cache.incr(cache_key)

        if count > limit:
            ttl = cache.ttl(cache_key) if hasattr(cache, "ttl") else window
            return JsonResponse(
                {"detail": "Too many requests.", "retry_after": ttl},
                status=429,
                headers={"Retry-After": str(ttl)},
            )

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = str(max(0, limit - count))
        return response


    @staticmethod
    def _resolve_tier(request, path: str) -> str:
        for fragment, tier in _PATH_TIERS:
            if fragment in path:
                return tier
        return "user" if request.user.is_authenticated else "anon"

    @staticmethod
    def _parse_rate(tier: str) -> tuple[int, int]:
        rates = settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {})
        rate_str = rates.get(tier, "60/minute")
        limit_str, period = rate_str.split("/")
        return int(limit_str), _PERIOD_SECONDS.get(period, 60)

    @staticmethod
    def _identifier(request) -> str:
        if request.user.is_authenticated:
            return str(request.user.id)
        return request.META.get("REMOTE_ADDR", "unknown")