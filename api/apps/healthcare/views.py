"""Healthcare API: contacts, hospitals, emergency SMS."""

from __future__ import annotations

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.renderers import haversine_distance_km
from apps.healthcare.models import EmergencyContact, Hospital
from apps.healthcare.serializers import (
    EmergencyContactSerializer,
    EmergencyTriggerSerializer,
    HospitalSerializer,
)


class EmergencyContactListCreateView(generics.ListCreateAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmergencyContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmergencyContact.objects.filter(user=self.request.user)


class HospitalNearbyView(generics.ListAPIView):
    serializer_class = HospitalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Hospital.objects.all()

    def list(self, request, *args, **kwargs):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = request.query_params.get("radius_km", "25")
        filters_raw = request.query_params.get("filters", "")
        if lat is None or lng is None:
            return Response(
                {
                    "error": "lat and lng are required.",
                    "detail": "lat and lng are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            lat_f = float(lat)
            lng_f = float(lng)
            radius_f = float(radius)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Invalid coordinates or radius.",
                    "detail": "Invalid coordinates or radius.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = list(Hospital.objects.all())
        flags = {x.strip() for x in filters_raw.split(",") if x.strip()}
        nearby = []
        for h in qs:
            if "psychiatric" in flags and not h.has_psychiatric_emergency:
                continue
            if "pediatric" in flags and not h.has_pediatric_emergency:
                continue
            if "maternal" in flags and not h.has_maternal_emergency:
                continue
            d = haversine_distance_km(
                lat_f, lng_f, float(h.location_lat), float(h.location_lng)
            )
            if d <= radius_f:
                nearby.append((d, h))
        nearby.sort(key=lambda x: x[0])
        out = []
        for d, h in nearby:
            ser = HospitalSerializer(h).data
            ser["distance_km"] = round(d, 3)
            out.append(ser)
        return Response(out)


class EmergencyTriggerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        ser = EmergencyTriggerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        lat = ser.validated_data["location_lat"]
        lng = ser.validated_data["location_lng"]
        user = request.user
        user_name = str(user.phone)
        phones = []
        if user.support_person_phone:
            phones.append(user.support_person_phone)
        if user.ob_phone:
            phones.append(user.ob_phone)
        if not phones:
            return Response(
                {
                    "error": "No emergency numbers on profile.",
                    "detail": "Add support or OB phone first.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        for p in phones:
            pass
        #     send_emergency_sms.delay(p, user_name, lat, lng)
        # return Response({"detail": "Emergency messages queued."}, status=status.HTTP_202_ACCEPTED)
