from rest_framework import generics, status
from rest_framework.response import Response

from .models import MumTalkPost
from .serializers import MumTalkPostSerializer


class MumTalkPostCreateView(APIView):
    
    def post(self, request):
        serializer = MumTalkPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

