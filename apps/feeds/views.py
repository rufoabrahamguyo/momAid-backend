from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import cloudinary.uploader

from .serializers import VideoSerializer,CommentSerializer, CommentListSerializer
from .models import Video, Comment
from .paginator import VideoCursorPaginator, CommentLimitPaginator
from django.shortcuts import get_object_or_404

class UploadUserVideoView(APIView):
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            video_file = serializer.validated_data.get('video_file_path')

            video = serializer.save(user=request.user, video_file=video_file)
            
            return Response(VideoSerializer(video).data, status=201)

class UserSpecificVideoView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):

        try: 
            user = request.user
            videos = user.videos.select_related('attributes').all().order_by('-created_at')

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(videos, request)

            if page is not None:
                serializer = VideoSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response(serializer.data)
                
            serializer = VideoSerializer(videos, many=True, context={'request': request})
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({'detail': str(e)}, status=500)

class GetAllVideosView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):
        try:
            videos = Video.objects.select_related('attributes', 'user').order_by('-created_at')

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(videos, request)

            if page is not None:
                serializer = VideoSerializer(page, many=True, context={'request': request})
                
                return paginator.get_paginated_response(serializer.data)

            serializer = VideoSerializer(videos, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        
        except Exception as e:
            return Response({'detail': f"Database error: {str(e)}"}, status=500)
    
class CreateVideoCommentView(APIView):

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(user=request.user, video=video)

            return Response({
                "comment": comment.content,
                "posted_at": comment.created_at
            }, status=201)

        return Response(serializer.errors, status=400)


class ReplyCommentView(APIView):

    def post(self, request, comment_id):

        parent_comment = get_object_or_404(Comment, id=comment_id)

        if parent_comment.parent is not None:
            return Response(
                {"detail": "Only 1 level replies allowed"},
                status=400
            )

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(
                user=request.user,
                video=parent_comment.video,
                parent=parent_comment
            )

            return Response({
                "comment": comment.content,
                "posted_at": comment.created_at
            }, status=201)

        return Response(serializer.errors, status=400)

        

class ListVideoCommentsView(APIView):
    pagination_class = CommentLimitPaginator

    def get(self, request, video_id):

        video = get_object_or_404(Video, id=video_id)

        comments = Comment.objects.filter(
            video=video,
            parent__isnull=True
        ).select_related('user').prefetch_related("replies", "replies__user")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(comments, request)

        if page is not None:
            serializer = CommentListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = CommentListSerializer(comments, many=True, context={'request': request})

        return Response(serializer.data, status=200)
