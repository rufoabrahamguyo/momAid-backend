from rest_framework import serializers
from .models import VideoAttributes, Video, Comment


class VideoAttributesSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoAttributes
        fields = [
            "public_id",
            "title",
            "description",
            "duration",
            "size",
        ]
        read_only_fields = [
            "public_id",
            "duration",
            "size",
        ]


class VideoSerializer(serializers.ModelSerializer):
    attributes = VideoAttributesSerializer()
    video_file_path = serializers.FileField(write_only=True)

    class Meta:
        model = Video
        fields = ["public_id", "video_file", "user", "attributes", "video_file_path","created_at","updated_at",]
        read_only_fields = ["public_id", "user", "video_file","created_at","updated_at",]

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
        fields = ["public_id", "content", "created_at"]
        read_only_fields = ["public_id", "created_at"]


class ReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ["public_id", "content", "created_at"]


class CommentListSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "public_id",
            "content",
            "created_at",
            "replies"
        ]