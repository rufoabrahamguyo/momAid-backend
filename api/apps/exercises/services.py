import cloudinary.uploader

from .models import Exercise

MAX_SIZE = 5 * 1024 * 1024 * 1024
FILE_TYPES = [".mov", ".mp4"]

def create_exercise(user: User, file) -> str:

    if file.size > MAX_SIZE:
        raise ValueError('Please upload a shorter video')
    if file.content_type not in FILE_TYPES:
        raise ValueError('File format not supported')


    result = cloudinary.uploader.upload(
        file,
        folder="videos/",
        public_id=f"user_{user.public_id}",
        resource_type="video"
    )

    exercise = Excercise.objects.get_or_create(
        video_file=result["public_id"]
    )
    exercise.save()
    return result["secure_id"]
