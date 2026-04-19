"""Exercises API."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.exercises.models import Exercise
from apps.exercises.serializers import ExerciseSerializer


class ExerciseListView(generics.ListAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]
