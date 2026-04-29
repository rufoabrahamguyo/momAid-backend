from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PartnerTask, PartnerTaskCompletion

User = get_user_model()

class PartnerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerTask
        fields = [
            "id",
            "baby_age_weeks_min",
            "baby_age_weeks_max",
            "title",
            "description",
            "icon",
            "order",
            "is_recurring",
            "estimated_time",
            "why_it_matters",
        ]

        read_only_fields = ['id']

    def validate(self, data):
        if data['baby_age_weeks_min'] > data['baby_age_weeks_max']:
            raise serializers.ValidationError("Min week cannot be greater than Max week.")
        return data

class PartnerTaskCompletionSerializer(serializers.ModelSerializer):
    attrs = PartnerTaskSerializer(read_only=True)
    class Meta:
        model = PartnerTaskCompletion
        fields = [
            'id',
            'status',
            'completed_at',
            'attrs',
        ]


