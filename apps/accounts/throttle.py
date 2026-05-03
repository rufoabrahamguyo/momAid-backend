from rest_framework.throttling import AnonRateThrottle

class CustomRegistrationThrottle(AnonRateThrottle):
    scope = 'auth_limit'

    def get_cache_key(self, request, view):
        return "global_registration_total_count"