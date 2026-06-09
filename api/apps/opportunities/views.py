# """API views for opportunities."""

# from __future__ import annotations

# import csv

# from django.http import HttpResponse
# from django.utils import timezone
# from rest_framework import status, viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAdminUser, IsAuthenticated
# from rest_framework.response import Response

# from apps.opportunities.models import Opportunity, OpportunityInterest
# from apps.opportunities.serializers import (
#     OpportunitySerializer,
#     OpportunityWriteSerializer,
# )
# from apps.notifications.tasks import notify_admin_of_interest, send_opportunity_push_notification


# class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
#     """List and retrieve active opportunities; manage interest."""

#     serializer_class = OpportunitySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         now = timezone.now()
#         return Opportunity.objects.filter(is_filled=False, deadline__gt=now)

#     @action(detail=True, methods=["post", "delete"], url_path="interest")
#     def interest(self, request, pk=None) -> Response:
#         opportunity = self.get_object()
#         if request.method == "POST":
#             obj, created = OpportunityInterest.objects.get_or_create(
#                 opportunity=opportunity,
#                 user=request.user,
#             )
#             if created:
#                 notify_admin_of_interest.delay(opportunity.title, str(request.user.phone))
#                 send_opportunity_push_notification.delay(opportunity.title)
#             return Response({"detail": "Interest recorded."}, status=status.HTTP_200_OK)
#         deleted, _ = OpportunityInterest.objects.filter(
#             opportunity=opportunity,
#             user=request.user,
#         ).delete()
#         if not deleted:
#             return Response(
#                 {"error": "No interest found.", "detail": "No interest found."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class AdminOpportunityViewSet(viewsets.ModelViewSet):
#     """Full CRUD for staff."""

#     queryset = Opportunity.objects.all()
#     permission_classes = [IsAdminUser]

#     def get_serializer_class(self):
#         if self.action in ("create", "update", "partial_update"):
#             return OpportunityWriteSerializer
#         return OpportunitySerializer

#     def perform_create(self, serializer):
#         extra = {}
#         if self.request.user.is_authenticated:
#             extra["created_by"] = self.request.user
#         serializer.save(**extra)

#     @action(detail=True, methods=["get"], url_path="interests")
#     def interests(self, request, pk=None) -> HttpResponse:
#         """Return interests as CSV (admin)."""
#         opportunity = self.get_object()
#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = f'attachment; filename="opportunity-{opportunity.id}-interests.csv"'
#         writer = csv.writer(response)
#         writer.writerow(["opportunity_title", "user_phone", "user_email", "interested_at"])
#         for row in opportunity.interests.select_related("user"):
#             u = row.user
#             email = getattr(u, "ob_email", "") or ""
#             writer.writerow([opportunity.title, u.phone, email, row.created_at.isoformat()])
#         return response
