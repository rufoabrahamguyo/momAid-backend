from django.contrib import admin

from .models import Video, VideoAttributes


class VideoInline(admin.StackedInline):
    model = Video
    can_delete = False
    verbose_name = "Video File and User"
    verbose_name_plural = "Video File and User"
    extra = 0
    fields = ("user", "video_file")
    fk_name = "attributes"


@admin.register(VideoAttributes)
class VideoAttributesAdmin(admin.ModelAdmin):
    """
    This is now the primary admin for your videos.
    You edit the Title/Description here, and the file is attached below.
    """

    list_display = ("title", "get_email", "duration", "size")
    search_fields = ("title", "video__user__email")

    inlines = [VideoInline]

    fieldsets = (
        ("Basic Information", {"fields": ("title", "description")}),
        (
            "Metadata (Auto-generated)",
            {
                "fields": (
                    "duration",
                    "size",
                ),
                "classes": ("collapse"),
            },
        ),
    )

    readonly_fields = ("duration", "size")

    def get_email(self, obj):
        return obj.video.user.email if hasattr(obj, "video") else "No User"

    get_email.short_description = "Uploaded By"


@admin.register(Video)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ("video_file", "user")
    search_fields = ("user__email",)
