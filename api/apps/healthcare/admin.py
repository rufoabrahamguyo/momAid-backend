"""Admin for healthcare."""

from django.contrib import admin

from apps.healthcare.models import EmergencyContact, Hospital


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "phone", "is_primary")


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "has_psychiatric_emergency",
        "has_pediatric_emergency",
        "has_maternal_emergency",
    )
