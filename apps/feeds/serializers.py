from rest_framework import serializers
from .models import VideoAttributes, Video
import os


class VideoAttributesSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoAttributes
        fields = [
            "id",
            "title",
            "description",
            "duration",
            "size",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "duration",
            "size",
            "created_at",
            "updated_at",
        ]


class VideoSerializer(serializers.ModelSerializer):
    attributes = VideoAttributesSerializer()
    video_file_path = serializers.FileField(write_only=True)

    class Meta:
        model = Video
        fields = ["id", "video_file", "user", "attributes", "video_file_path"]
        read_only_fields = ["id", "user", "video_file"]

    def create(self, validated_data):
        # 1. Pop out the 'temporary' file path so we don't try to save it to the DB
        validated_data.pop('video_file_path', None)

        # 2. Extract the nested attribute dictionary (now includes duration/size from View)
        attr_data = validated_data.pop('attributes')
        
        # 3. Extract the user and the cloudinary URL
        user = validated_data.pop('user')
        video_url = validated_data.pop('video_file')

        # 4. Create the Attributes record first
        # This works because attr_data is a dict: {'title': '...', 'duration': 10, ...}
        attribute_instance = VideoAttributes.objects.create(**attr_data)

        # 5. Create the Video record and link the Attribute instance
        video = Video.objects.create(
            user=user,
            video_file=video_url,
            attributes=attribute_instance
        )
        
        return video