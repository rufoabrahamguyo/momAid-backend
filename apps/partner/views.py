from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PartnerTask, PartnerTaskCompletion, InviteCode

from .serializers import (
    PartnerTaskCompletionSerializer,
    PartnerTaskSerializer,
)


class GenerateCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user 

        try:
            InviteCode.objects.filter(creator=user).delete()

            new_invite = InviteCode.objects.create(creator=user)

            return Response({
                "code": new_invite.code, 
                "expires_at": new_invite.expires_at
            }, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class LinkPartnerView(APIView):

    def post(self, request):
        partner_code = request.data.get("invite_code", "").upper().strip()
        

        partner_profile = request.user.partner_profile

        try:
            invite = InviteCode.objects.get(code=partner_code)

            if invite.is_expired:
                invite.delete()
                return Response({'error': 'Code expired.'}, status=400)

            mother_user = invite.creator
            mother_profile = mother_user.mother_profile
            

            mother_profile.partner = partner_profile
            mother_profile.save()

            invite.delete()
            
            return Response({"message": "Successfully linked!"}, status=200)

        except InviteCode.DoesNotExist:
            return Response({"error": "Invalid code."}, status=404)

        
class CreatePartnerTaskView(APIView):

    def post(self, request):
        user = request.user

        if not user.is_staff:
            return Response({
                "detail": "Unathorized access detected"
            }, status=401)

        serializer = PartnerTaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response({
                'detail': 'Resource created successfully'
            }, status=201)
        return Response(serializer.errors, status=400)

class ListPartnerTaskView(APIView):
    def get(self, request):
        partner_profile = getattr(request.user, 'partner_profile', None)
        
        if not partner_profile:
            return Response({'detail': 'Partner profile not found.'}, status=404)

        mother = partner_profile.linked_mother

        if not mother:
            return Response({'detail': 'Link to a mother first'}, status=400)

        mother_current_week = mother.get_current_mother_week()

        tasks = PartnerTask.objects.filter(
            baby_age_weeks_min__lte=mother_current_week,
            baby_age_weeks_max__gte=mother_current_week
        )

        serializer = PartnerTaskSerializer(tasks, many=True)

        return Response(serializer.data, status=200)

class CreatePartnerTaskCompletionView(APIView):

    def post(self, request, task_id):

        status = request.data.get('status', 'completed')
        notes = request.data.get('notes', '')

        try:
            task = PartnerTask.objects.get(id=task_id)
        
        except PartnerTask.DoesNotExist:
            return Response({
                'detail': 'Task does not exist'
            }, status=404)

        user = request.user

        if user.role != 'partner':
            return Response({'detail': 'Only partners can complete these tasks'}, status=403)
        
        completion, created= PartnerTaskCompletion.objects.get_or_create(
            partner=user,
            task=task,
            defaults={
                'status': status,
                'notes': notes
            }
        )

        if not created:
            return Response({'detail': 'Task already marked as completed'}, status=200)

        return Response({'detail': 'Task completed successfully'}, status=201)

class ListPartnerTaskCompletion(APIView):

    def get(self, request):
        user = request.user

        if user.role != 'partner':
            return Response({'detail': 'Only partners can complete these tasks'}, status=403)

        tasks = PartnerTaskCompletion.objects.all().filter(partner=user)
        
        serializer = PartnerTaskCompletionSerializer(tasks, many=True)

        return Response(serializer.data, status=200)


class ListAdminPartnerTasksView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PartnerTaskSerializer
    queryset = PartnerTask.objects.all()


    




