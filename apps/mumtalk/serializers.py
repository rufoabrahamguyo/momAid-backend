from rest_framework import serializers

from .models import MumTalkPost


class MumTalkPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = MumTalkPost
        fields = [
            "public_id",
            "author",
            "title"
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "public_id",
            "author",
            "created_at",
            "updated_at",
        ]
