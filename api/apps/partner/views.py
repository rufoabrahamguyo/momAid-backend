import logging
from datetime import timedelta, timezone

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InviteCode, PartnerTask, PartnerTaskCompletion
from .paginator import TaskLimitPaginator
from .serializers import (
    PartnerTaskCompletionSerializer,
    PartnerTaskSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class GenerateCodeView(APIView):
    def post(self, request):

        try:
            new_invite, created = InviteCode.objects.update_or_create(
                creator=request.user,
                defaults={
                    "code": InviteCode.generate_unique_code(),
                    "expires_at": timezone.now() + timedelta(hours=2),
                },
            )

            return Response(
                {"code": new_invite.code, "expires_at": new_invite.expires_at},
                status=200,
            )

        except Exception:
            logger.exception(
                "Failed to generate invite code for user %s", request.user.id
            )
            return Response(
                {"error": "An internal error occurred. Please try again later."},
                status=500,
            )


class LinkPartnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partner_code = request.data.get("invite_code", "").upper().strip()
        partner_profile = getattr(request.user, "partner_profile", None)

        if not partner_profile:
            return Response({"detail": "Partner profile not found"}, status=404)

        try:
            invite = InviteCode.objects.select_related("creator__mother_profile").get(
                code=partner_code
            )

            if invite.is_expired:
                invite.delete()
                return Response({"error": "Code expired."}, status=400)

            mother_profile = getattr(invite.creator, "mother_profile", None)
            if not mother_profile:
                return Response({"detail": "Mother profile not found"}, status=404)

            with transaction.atomic():
                mother_profile.partner = partner_profile
                mother_profile.save()
                invite.delete()

            return Response({"message": "Successfully linked!"}, status=200)

        except InviteCode.DoesNotExist:
            return Response({"error": "Invalid code."}, status=404)


class CreatePartnerTaskView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):

        serializer = PartnerTaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({"detail": "Resource created successfully"}, status=201)

        return Response(serializer.errors, status=400)


class ListPartnerTaskView(APIView):
    pagination_class = TaskLimitPaginator

    def get(self, request):
        partner_profile = getattr(request.user, "partner_profile", None)

        if not partner_profile:
            return Response({"detail": "Partner profile not found."}, status=404)

        mother = partner_profile.linked_mother

        if not mother:
            return Response({"detail": "Link to a mother first"}, status=400)

        mother_current_week = mother.get_current_mother_week()

        tasks = PartnerTask.objects.filter(
            baby_age_weeks_min__lte=mother_current_week,
            baby_age_weeks_max__gte=mother_current_week,
        ).order_by("id")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tasks, request)

        if page is not None:
            serializer = PartnerTaskSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PartnerTaskSerializer(tasks, many=True)

        return Response(serializer.data, status=200)


class CreatePartnerTaskCompletionView(APIView):

    def post(self, request, task_id):

        status = request.data.get("status", "completed")
        notes = request.data.get("notes", "")

        try:
            task = PartnerTask.objects.get(id=task_id)

        except PartnerTask.DoesNotExist:
            return Response({"detail": "Task does not exist"}, status=404)

        user = request.user

        if user.role != "partner":
            return Response(
                {"detail": "Only partners can complete these tasks"}, status=403
            )

        completion, created = PartnerTaskCompletion.objects.get_or_create(
            partner=user, task=task, defaults={"status": status, "notes": notes}
        )

        if not created:
            return Response({"detail": "Task already marked as completed"}, status=200)

        return Response({"detail": "Task completed successfully"}, status=201)


class ListPartnerTaskCompletion(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TaskLimitPaginator

    def get(self, request):
        user = request.user
        if user.role != "partner":
            return Response({"detail": "Access denied"}, status=403)

        tasks = PartnerTaskCompletion.objects.filter(partner=user).order_by("-id")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tasks, request)

        if page is not None:
            serializer = PartnerTaskCompletionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PartnerTaskCompletionSerializer(tasks, many=True)
        return Response(serializer.data, status=200)


class ListAdminPartnerTasksView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PartnerTaskSerializer
    queryset = PartnerTask.objects.all()
