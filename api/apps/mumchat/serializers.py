from rest_framework import serializers

from .models import MumChatPost, MumChatReply


class MumChatReplySerializer(serializers.ModelSerializer):
    is_root_reply = serializers.BooleanField(read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = MumChatReply
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
        return MumChatReplySerializer(children, many=True).data

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Reply cannot be blank.")
        return value.strip()


class MumChatCreateReplySerializer(serializers.ModelSerializer):

    class Meta:
        model = MumChatReply
        fields = ["content"]

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Reply cannot be blank.")
        return value.strip()


class MumChatPostSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MumChatPost
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
        return MumChatReplySerializer(root_replies, many=True).data

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be blank.")
        return value.strip()

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()
