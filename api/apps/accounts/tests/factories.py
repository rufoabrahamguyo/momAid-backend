import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.accounts.models import MotherProfile, PartnerProfile

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Faker("first_name")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    role = User.Role.MOTHER
    is_active = True


class MotherUserFactory(UserFactory):
    role = User.Role.MOTHER

    profile = factory.RelatedFactory(
        "api.apps.accounts.tests.factories.MotherProfileFactory",
        factory_related_name="user",
    )


class PartnerUserFactory(UserFactory):
    role = User.Role.PARTNER

    profile = factory.RelatedFactory(
        "api.apps.accounts.tests.factories.PartnerProfileFactory",
        factory_related_name="user",
    )


class InactiveUserFactory(UserFactory):
    is_active = False


class MotherProfileFactory(DjangoModelFactory):
    class Meta:
        model = MotherProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory, role=User.Role.MOTHER)
    baby_due_date = factory.Faker("future_date", end_date="+280d")
    baby_birth_date = None


class PartnerProfileFactory(DjangoModelFactory):
    class Meta:
        model = PartnerProfile
        django_get_or_create = ("user",)

    user = factory.SubFactory(UserFactory, role=User.Role.PARTNER)
