"""Remedies API."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.remedies.models import BabyCondition
from apps.remedies.serializers import BabyConditionSerializer


class BabyConditionListView(generics.ListAPIView):
    """List all conditions with nested remedies."""

    queryset = BabyCondition.objects.prefetch_related("remedies")
    serializer_class = BabyConditionSerializer
    permission_classes = [IsAuthenticated]
