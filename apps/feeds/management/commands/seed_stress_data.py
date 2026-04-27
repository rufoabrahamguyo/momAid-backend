import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.feeds.models import Video, Comment

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with data for load testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Get or Create a Load Test User
        user, created = User.objects.get_or_create(
            email="testuser@mumaid.com",
            defaults={
                "username": "testuser",
                "is_active": True,
                "role": "mother" # Matching your GoogleSocialLoginView logic
            }
        )
        if created:
            user.set_password("securepassword123")
            user.save()

        # 2. Create Videos
        # We create 200 videos to give the database enough 'weight'
        video_objs = []
        for i in range(200):
            video_objs.append(Video(
                user=user,
                video_file="https://res.cloudinary.com/demo/video/upload/sample.mp4",
                # Add any other required fields from your Video model here
            ))
        
        # bulk_create is much faster for stress testing
        created_videos = Video.objects.bulk_create(video_objs)
        self.stdout.write(f"Created {len(created_videos)} videos.")

        # 3. Create Comments
        comment_objs = []
        videos = Video.objects.all()
        for video in videos:
            # Create 5-10 comments per video
            for j in range(random.randint(5, 10)):
                comment_objs.append(Comment(
                    user=user,
                    video=video,
                    content=f"Stress test comment {j} for video {video.id}"
                ))

        Comment.objects.bulk_create(comment_objs)
        self.stdout.write(f"Successfully seeded {Comment.objects.count()} comments!")