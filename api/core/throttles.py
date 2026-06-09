from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class OtpRateThrottle(AnonRateThrottle):
    scope = "otp_limit"


class LoginRateThrottle(AnonRateThrottle):
    scope = "login_limit"


class AuthRateThrottle(UserRateThrottle):
    scope = "auth_limit"


class UploadRateThrottle(UserRateThrottle):
    scope = "upload_limit"