from rest_framework import serializers
from .models import VideoAttributes, Video, Comment


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
        validated_data.pop('video_file_path', None)

        attr_data = validated_data.pop('attributes')
        user = validated_data.pop('user')
        video_url = validated_data.pop('video_file')

        attribute_instance = VideoAttributes.objects.create(**attr_data)

        video = Video.objects.create(
            user=user,
            video_file=video_url,
            attributes=attribute_instance
        )

        return video


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at"]


class CommentListSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "created_at",
            "replies"
        ]