from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle

from .models import MumTalkPost, MumTalkReply                  # fix: MumTalkReply was missing
from .serializers import MumTalkPostSerializer, MumTalkCreateReplySerializer
from .utils import hash_user_identity


class MumTalkPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MumTalkPostCreateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        author_hash = hash_user_identity(request.user.id)
        serializer = MumTalkPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author_hash=author_hash)
            return Response({"detail": "Post created successfully."}, status=201)
        return Response(serializer.errors, status=400)


class MumTalkPostListView(APIView):

    def get(self, request):
        posts = MumTalkPost.objects.all()
        paginator = MumTalkPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = MumTalkPostSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MumTalkPostDetailView(APIView):

    def get(self, request, post_id):
        post = get_object_or_404(MumTalkPost, public_id=post_id)
        serializer = MumTalkPostSerializer(post)                # replies already nested inside serializer
        return Response(serializer.data, status=200)


class MumTalkPostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, post_id):                          # fix: patch is more appropriate than put
        author_hash = hash_user_identity(request.user.id)
        post = get_object_or_404(MumTalkPost, public_id=post_id, author_hash=author_hash)
        serializer = MumTalkPostSerializer(instance=post, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'detail': 'Post updated successfully.'}, status=200)
        return Response(serializer.errors, status=400)


class MumTalkPostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        author_hash = hash_user_identity(request.user.id)
        post = get_object_or_404(MumTalkPost, public_id=post_id, author_hash=author_hash)
        post.delete()
        return Response(status=204)


class MumTalkListUserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        author_hash = hash_user_identity(request.user.id)
        posts = MumTalkPost.objects.filter(author_hash=author_hash)
        paginator = MumTalkPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = MumTalkPostSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class MumTalkReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    MAX_REPLY_DEPTH = 5

    def get_reply_depth(self, reply):
        depth = 0
        current = reply
        while current.parent_reply is not None:               
            depth += 1
            current = current.parent_reply
            if depth >= self.MAX_REPLY_DEPTH:
                break
        return depth                                          

    def post(self, request, post_id):
        author_replier_hash = hash_user_identity(request.user.id)
        parent_post = get_object_or_404(MumTalkPost, public_id=post_id)

        parent_reply = None
        parent_id = request.data.get('parent_id')

        if parent_id:
            parent_reply = get_object_or_404(
                MumTalkReply,
                public_id=parent_id,
                post=parent_post                               
            )
            if self.get_reply_depth(parent_reply) >= self.MAX_REPLY_DEPTH:
                return Response(
                    {"detail": f"Maximum reply depth of {self.MAX_REPLY_DEPTH} reached."},
                    status=400
                )

        serializer = MumTalkCreateReplySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            reply = serializer.save(
                author_replier_hash=author_replier_hash,
                post=parent_post,
                parent_reply=parent_reply                      
            )
            return Response({
                "reply": reply.content,
                "posted_at": reply.created_at
            }, status=201)

        return Response(serializer.errors, status=400)