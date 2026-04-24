"""Django admin for opportunities."""

import csv

from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html

from apps.opportunities.models import Opportunity, OpportunityInterest


class OpportunityInterestInline(admin.TabularInline):
    model = OpportunityInterest
    extra = 0
    fields = ("user", "contact_preference", "created_at")
    readonly_fields = ("user", "created_at")
    can_delete = False


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "deadline",
        "is_filled",
        "interested_count",
        "is_active_display",
        "created_at",
    )
    list_filter = ("is_filled", "created_at")
    search_fields = ("title", "description")
    date_hierarchy = "deadline"
    inlines = [OpportunityInterestInline]
    actions = ("export_interests_csv", "mark_as_filled")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_interest_count=Count("interests"))

    @admin.display(description="Interested")
    def interested_count(self, obj: Opportunity) -> int:
        return getattr(obj, "_interest_count", obj.interests.count())

    @admin.display(description="Active", boolean=True)
    def is_active_display(self, obj: Opportunity) -> bool:
        return obj.is_active

    @admin.action(description="Export interests for selected opportunities (CSV)")
    def export_interests_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="opportunity-interests.csv"'
        writer = csv.writer(response)
        writer.writerow(["opportunity_title", "user_phone", "user_email", "interested_at"])
        for opp in queryset:
            for row in opp.interests.select_related("user"):
                u = row.user
                email = getattr(u, "ob_email", "") or ""
                writer.writerow([opp.title, u.phone, email, row.created_at.isoformat()])
        return response

    @admin.action(description="Mark selected as filled")
    def mark_as_filled(self, request, queryset):
        updated = queryset.update(is_filled=True)
        self.message_user(request, f"{updated} opportunities marked as filled.")


@admin.register(OpportunityInterest)
class OpportunityInterestAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "user", "created_at")
    search_fields = ("opportunity__title", "user__phone")
