"""Admin for milk listings."""

from django.contrib import admin

from apps.milk_support.models import MilkListing


@admin.register(MilkListing)
class MilkListingAdmin(admin.ModelAdmin):
    list_display = (
        "listing_type",
        "user",
        "quantity_ml",
        "is_active",
        "expiration_date",
        "created_at",
    )
    list_filter = ("listing_type", "is_active")
