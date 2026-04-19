"""Root URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/opportunities/", include("apps.opportunities.urls")),
    path("api/admin/opportunities/", include("apps.opportunities.admin_urls")),
    path("api/remedies/", include("apps.remedies.urls")),
    path("api/exercises/", include("apps.exercises.urls")),
    path("api/milk/", include("apps.milk_support.urls")),
    path("api/partner/", include("apps.partner.urls")),
    path("api/healthcare/", include("apps.healthcare.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
