"""Admin for remedies."""

from django.contrib import admin

from apps.remedies.models import BabyCondition, Remedy


class RemedyInline(admin.TabularInline):
    model = Remedy
    extra = 0


@admin.register(BabyCondition)
class BabyConditionAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order")
    inlines = [RemedyInline]


@admin.register(Remedy)
class RemedyAdmin(admin.ModelAdmin):
    list_display = ("title", "condition", "order")
