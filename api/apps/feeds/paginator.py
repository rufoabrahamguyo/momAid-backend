from rest_framework.pagination import CursorPagination, LimitOffsetPagination


class VideoCursorPaginator(CursorPagination):
    page_size = 10
    ordering = ["-created_at", "id"]


class CommentLimitPaginator(LimitOffsetPagination):
    default_limit = 10
    max_limit = 50
