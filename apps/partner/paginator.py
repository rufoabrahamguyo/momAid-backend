from rest_framework.pagination import LimitOffsetPagination

class TaskLimitPaginator(LimitOffsetPagination):
    default_limit = 10
    max_limit = 20


