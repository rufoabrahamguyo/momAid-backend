"""Public opportunity routes."""

from rest_framework.routers import DefaultRouter

from apps.opportunities import views

router = DefaultRouter()
router.register(r"", views.OpportunityViewSet, basename="opportunity")

urlpatterns = router.urls
