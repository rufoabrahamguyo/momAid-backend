from rest_framework import serializers
from .models import MumTalkPost, MumTalkReply


class MumTalkReplySerializer(serializers.ModelSerializer):
    is_root_reply = serializers.BooleanField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = MumTalkReply
        fields = [
            "public_id",
            "content",
            "parent_reply",
            "is_root_reply",
            "children",
            "created_at",
        ]
        read_only_fields = ["public_id", "is_root_reply", "children", "created_at"]

    def get_children(self, obj):
        children = obj.children.all()
        return MumTalkReplySerializer(children, many=True).data

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reply cannot be blank.")
        return value.strip()


class MumTalkCreateReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = MumTalkReply
        fields = ["content"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Reply cannot be blank.")
        return value.strip()


class MumTalkPostSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MumTalkPost
        fields = [
            "public_id",
            "title",
            "content",
            "reply_count",
            "replies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "public_id",
            "reply_count",
            "replies",
            "created_at",
            "updated_at",
        ]

    def get_replies(self, obj):
        root_replies = obj.replies.filter(parent_reply=None)
        return MumTalkReplySerializer(root_replies, many=True).data

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Content cannot be blank.")
        return value.strip()

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()
