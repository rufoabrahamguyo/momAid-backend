import pytest
from rest_framework.test import APIClient
from .factories import MotherUserFactory, PartnerUserFactory, InactiveUserFactory
from rest_framework.throttling import BaseThrottle
from django.core.cache import cache


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def mother_user(db):
    return MotherUserFactory()


@pytest.fixture
def partner_user(db):
    return PartnerUserFactory()


@pytest.fixture
def inactive_user(db):
    return InactiveUserFactory()


@pytest.fixture
def auth_client(api_client, mother_user):
    api_client.force_authenticate(user=mother_user)
    return api_client


@pytest.fixture
def partner_auth_client(api_client, partner_user):
    api_client.force_authenticate(user=partner_user)
    return api_client


# @pytest.fixture(autouse=True)
# def disable_all_throttling(monkeypatch):

#     from rest_framework.views import APIView
#     monkeypatch.setattr(APIView, "check_throttles", lambda self, request: None)


#     monkeypatch.setattr(BaseThrottle, "allow_request", lambda self, request, view: True)


@pytest.fixture(autouse=True)
def reset_throttle_cache():

    cache.clear()
    yield
