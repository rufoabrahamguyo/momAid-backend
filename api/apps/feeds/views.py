from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import cloudinary.uploader

from .serializers import (
    VideoSerializer,
    CommentSerializer,
    CommentListSerializer,
    VideoHistorySerializer,
)
from .models import Video, Comment, VideoHistory
from .paginator import VideoCursorPaginator, CommentLimitPaginator
from django.shortcuts import get_object_or_404
from django.db.models import F, Q


class UploadUserVideoView(APIView):
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            video_file = serializer.validated_data.get("video_file_path")

            video = serializer.save(user=request.user, video_file=video_file)

            return Response(VideoSerializer(video).data, status=201)


class UserSpecificVideoView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):

        try:
            user = request.user
            videos = (
                user.videos.select_related("attributes").all().order_by("-created_at")
            )

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(videos, request)

            if page is not None:
                serializer = VideoSerializer(
                    page, many=True, context={"request": request}
                )
                return paginator.get_paginated_response(serializer.data)

            serializer = VideoSerializer(
                videos, many=True, context={"request": request}
            )
            return Response(serializer.data, status=200)

        except Exception:
            return Response({"detail": "An internal error has occurred."}, status=500)


class GetAllVideosView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):
        try:
            videos = Video.objects.select_related("attributes", "user").order_by(
                "-created_at"
            )

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(videos, request)

            if page is not None:
                serializer = VideoSerializer(
                    page, many=True, context={"request": request}
                )

                return paginator.get_paginated_response(serializer.data)

            serializer = VideoSerializer(
                videos, many=True, context={"request": request}
            )
            return Response(serializer.data, status=200)

        except Exception:
            return Response({"detail": "An internal error has occurred."}, status=500)


class CreateVideoCommentView(APIView):

    def post(self, request, video_id):
        video = get_object_or_404(Video, id=video_id)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(user=request.user, video=video)

            return Response(
                {"comment": comment.content, "posted_at": comment.created_at},
                status=201,
            )

        return Response(serializer.errors, status=400)


class ReplyCommentView(APIView):

    def post(self, request, comment_id):

        parent_comment = get_object_or_404(Comment, id=comment_id)

        if parent_comment.parent is not None:
            return Response({"detail": "Only 1 level replies allowed"}, status=400)

        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(
                user=request.user, video=parent_comment.video, parent=parent_comment
            )

            return Response(
                {"comment": comment.content, "posted_at": comment.created_at},
                status=201,
            )

        return Response(serializer.errors, status=400)


class ListVideoCommentsView(APIView):
    pagination_class = CommentLimitPaginator

    def get(self, request, video_id):

        video = get_object_or_404(Video, id=video_id)

        comments = (
            Comment.objects.filter(video=video, parent__isnull=True)
            .select_related("user")
            .prefetch_related("replies", "replies__user")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(comments, request)

        if page is not None:
            serializer = CommentListSerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = CommentListSerializer(
            comments, many=True, context={"request": request}
        )

        return Response(serializer.data, status=200)


class CreateVideoHistoryView(APIView):

    def post(self, request, video_id):

        progress = request.data.get("last_watched_at", 0.0)

        try:
            video_obj = Video.objects.get(public_id=video_id)

        except Video.DoesNotExist:
            return Response({"detail": "Video not found"}, status=404)

        video, created = VideoHistory.objects.update_or_create(
            user=request.user, video=video_obj, defaults={"last_watched_at": progress}
        )

        if not video:
            return Response({"detail": "Couldn't save video"}, status=400)

        return Response({"detail": "Successfully saved video"}, status=201)


class ContinueWatchingView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):
        history_queryset = (
            VideoHistory.objects.filter(user=request.user)
            .filter(
                Q(last_watched_at__gt=0)
                & Q(last_watched_at__lt=F("video__attributes__duration"))
            )
            .select_related("video", "video__attributes")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(history_queryset, request)

        if page is not None:
            serializer = VideoHistorySerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = VideoHistorySerializer(
            history_queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=200)


class ListVideoHistoryView(APIView):
    pagination_class = VideoCursorPaginator

    def get(self, request):
        history_queryset = VideoHistory.objects.filter(
            user=request.user
        ).select_related("video", "video__attributes")

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(history_queryset, request)

        if page is not None:
            serializer = VideoHistorySerializer(
                page, many=True, context={"request": request}
            )
            return paginator.get_paginated_response(serializer.data)

        serializer = VideoHistorySerializer(
            history_queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=200)
