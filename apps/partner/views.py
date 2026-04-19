"""Partner connect and task APIs."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.partner.models import PartnerTask, PartnerTaskCompletion
from apps.partner.permissions import IsPartner
from apps.partner.serializers import (
    ConnectSerializer,
    PartnerTaskCompletionSerializer,
    PartnerTaskSerializer,
)

User = get_user_model()


class PartnerConnectView(APIView):
    permission_classes = [IsAuthenticated, IsPartner]

    def post(self, request) -> Response:
        ser = ConnectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        code = ser.validated_data["unique_code"].strip()
        mother = get_object_or_404(User, unique_code=code, role=User.Role.MOTHER)
        mother.partner = request.user
        mother.save()
        return Response({"detail": "Connected.", "mother_id": mother.id}, status=status.HTTP_200_OK)


class PartnerTaskListView(generics.ListAPIView):
    serializer_class = PartnerTaskSerializer
    permission_classes = [IsAuthenticated, IsPartner]

    def get_queryset(self):
        qs = PartnerTask.objects.all()
        weeks = self.request.query_params.get("baby_age_weeks")
        if weeks is None:
            return qs
        try:
            w = int(weeks)
        except (TypeError, ValueError):
            return PartnerTask.objects.none()
        return qs.filter(baby_age_weeks_min__lte=w, baby_age_weeks_max__gte=w)


class PartnerTaskCompleteView(APIView):
    permission_classes = [IsAuthenticated, IsPartner]

    def post(self, request, pk: int) -> Response:
        task = get_object_or_404(PartnerTask, pk=pk)
        completion = PartnerTaskCompletion.objects.create(partner=request.user, task=task)
        data = PartnerTaskCompletionSerializer(completion).data
        return Response(data, status=status.HTTP_201_CREATED)


class PartnerCompletionListView(generics.ListAPIView):
    serializer_class = PartnerTaskCompletionSerializer
    permission_classes = [IsAuthenticated, IsPartner]

    def get_queryset(self):
        return PartnerTaskCompletion.objects.filter(partner=self.request.user).select_related("task")
