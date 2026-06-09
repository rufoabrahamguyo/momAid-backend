"""Milk listing API with nearby search."""

from __future__ import annotations

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.renderers import haversine_distance_km
from apps.milk_support.models import MilkListing
from apps.milk_support.serializers import MilkListingCreateSerializer, MilkListingSerializer


class MilkListingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MilkListingCreateSerializer
        return MilkListingSerializer

    def get_queryset(self):
        return MilkListing.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = request.query_params.get("radius_km", "50")
        qs = list(self.filter_queryset(self.get_queryset()))
        if lat is None or lng is None:
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data)
        try:
            lat_f = float(lat)
            lng_f = float(lng)
            radius_f = float(radius)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid lat, lng, or radius_km.", "detail": "Invalid lat, lng, or radius_km."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        nearby = []
        for obj in qs:
            d = haversine_distance_km(
                lat_f,
                lng_f,
                float(obj.location_lat),
                float(obj.location_lng),
            )
            if d <= radius_f:
                nearby.append((d, obj))
        nearby.sort(key=lambda x: x[0])
        data = []
        for d, obj in nearby:
            ser = MilkListingSerializer(obj).data
            ser["distance_km"] = round(d, 3)
            data.append(ser)
        return Response(data)


class MilkListingRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = MilkListing.objects.all()
    serializer_class = MilkListingSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            raise PermissionDenied("You can only delete your own listing.")
        return super().destroy(request, *args, **kwargs)
