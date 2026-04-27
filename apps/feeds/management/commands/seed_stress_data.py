import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.feeds.models import Video, Comment, VideoAttributes

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with data for load testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Get or Create a Load Test User
        # REMOVED 'username' because your model doesn't use it
        user, created = User.objects.get_or_create(
            email="testuser@mumaid.com",
            defaults={
                "is_active": True,
                # "role": "mother" # Uncomment if your User model actually has a 'role' field
            }
        )
        if created:
            user.set_password("securepassword123")
            user.save()
            self.stdout.write("Created test user.")

        # 2. Create Videos and Attributes
        # Since Video has a OneToOne with VideoAttributes, we must create both
        for i in range(100):
            attr = VideoAttributes.objects.create(
                title=f"Stress Test Video {i}",
                description="Automated description for load testing.",
                duration=random.uniform(10.0, 300.0),
                size=random.randint(1000000, 50000000)
            )
            
            video = Video.objects.create(
                user=user,
                video_file="https://res.cloudinary.com/demo/video/upload/sample.mp4",
                attributes=attr
            )

            # 3. Create 5 comments per video
            for j in range(5):
                Comment.objects.create(
                    user=user,
                    video=video,
                    content=f"Stress test comment {j} for video {video.id}"
                )

        self.stdout.write(f"Successfully seeded {Video.objects.count()} videos and their comments!")