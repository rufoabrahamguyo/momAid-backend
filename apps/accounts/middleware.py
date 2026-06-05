from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication 

class MomAidGlobalRateLimiter:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        if not request.user.is_authenticated:
            try:
                authenticator = JWTAuthentication()
                user_auth_tuple = authenticator.authenticate(request)
                if user_auth_tuple:
                    request.user = user_auth_tuple[0]
            except Exception:
                pass 

        if any(path.startswith(p) for p in ['/admin/', '/static/', '/media/', '/api/docs/']):
            return self.get_response(request)

        if "/v1/login/" in path or "/v1/register/" in path:
            tier = 'login_limit'
        elif "/v1/resend-otp/" in path or "/v1/verify/token/" in path:
            tier = 'otp_limit'
        elif "/v1/profile/image/" in path:
            tier = 'upload_limit'
        elif any(p in path for p in ['/healthcare/', '/partner/', '/milk/', '/opportunities/']):
            tier = 'auth_limit' 
        elif any(p in path for p in ['/feeds/', '/remedies/', '/exercises/', '/v1/whoami/', '/mumtalk/']):
            tier = 'user' if request.user.is_authenticated else 'anon'
        else:

            tier = 'user' if request.user.is_authenticated else 'anon'

        rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        rate_str = rates.get(tier, "2/min") 
        
        limit_val, period = rate_str.split('/')
        limit = int(limit_val)

        seconds_map = {'minute': 60, 'hour': 3600, 'day': 86400, 'min': 60}
        window = seconds_map.get(period, 60)


        identifier = request.user.id if request.user.is_authenticated else user_ip
        cache_key = f"rl:{tier}:{identifier}"
        print(f"DEBUG: Path {path} is using tier: {tier}")

        cache.get_or_set(cache_key, 0, window)
        current_count = cache.incr(cache_key)

        if current_count > limit:
            retry_after = getattr(cache, 'ttl', lambda x: window)(cache_key)
            # Create a response specifically for the error
            response = JsonResponse({
                "detail": f"Request limit exceeded for {tier}.",
                "retry_after": retry_after
            }, status=429)
            
    
            response['X-MomAid-Retry-After'] = str(retry_after)
            return response


        response = self.get_response(request)

        response['X-MomAid-Tier'] = tier
        response['X-MomAid-Limit'] = str(limit)
        response['X-MomAid-Remaining'] = str(max(0, limit - current_count))
        
        return response