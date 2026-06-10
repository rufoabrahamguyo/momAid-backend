from core.exceptions import MomAidException, ConflictError
from rest_framework import status


class UserAlreadyExists(ConflictError):
    default_detail = "An account with this email already exists."


class InvalidOTP(MomAidException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid or expired verification code."


class AccountNotActive(MomAidException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Account is not active."


class ProfileNotFound(MomAidException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Profile not found."
