from rest_framework.views import APIView       
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MumTalkPost
from .serializers import MumTalkPostSerializer
from .utils import hash_user_identity


class MumTalkPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MumTalkPostCreateView(APIView):
    permission_classes = [IsAuthenticated]  

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
        try:
            post = MumTalkPost.objects.get(public_id=post_id)
            serializer = MumTalkPostSerializer(post)
            return Response(serializer.data, status=200)
        except MumTalkPost.DoesNotExist:
            return Response({'detail': 'Post not found.'}, status=404)

class MumTalkPostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id):
        try:
            author_hash = hash_user_identity(request.user.id)
            post = MumTalkPost.objects.get(public_id=post_id, author_hash=author_hash)
        except MumTalkPost.DoesNotExist:
            return Response(
                {'detail': 'Post not found or you do not have permission to edit this post.'},
                status=404
            )

        serializer = MumTalkPostSerializer(instance=post, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'detail': 'Post updated successfully'
            }, status=200)


class MumTalkPostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id): 
        try:
            author_hash = hash_user_identity(request.user.id)
            post = MumTalkPost.objects.get(public_id=post_id, author_hash=author_hash)
            post.delete()
            return Response(status=204)
        except MumTalkPost.DoesNotExist:
            return Response(
                {'detail': 'Post not found or you do not have permission to delete this post.'},
                status=404
            )


class MumTalkListUserPostsView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        author_hash = hash_user_identity(request.user.id)
        posts = MumTalkPost.objects.filter(author_hash=author_hash)

        paginator = MumTalkPagination()
        page = paginator.paginate_queryset(posts, request)
        serializer = MumTalkPostSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)