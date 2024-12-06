from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
