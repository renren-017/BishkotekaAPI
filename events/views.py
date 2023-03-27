from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter

from events.models import OneTimeEvent, RegularEvent, Category
from events.serializers import OneTimeEventSerializer, RegularEventSerializer, CategorySerializer, \
    EventCommentSerializer
from utils.db.queries import get_events


class EventAPIView(APIView):
    serializer_class = OneTimeEventSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthenticated,)
    model = OneTimeEvent

    @extend_schema(
        responses=serializer_class(many=True),
        parameters=[
            OpenApiParameter(name='limit', type=int),
            OpenApiParameter(name='offset', type=int),
            OpenApiParameter(name='keyword', type=str),
            OpenApiParameter(name='category', type=int)
        ]
    )
    def get(self, request):
        self.check_permissions(request)
        paginator = self.pagination_class()
        search_keyword = request.query_params.get('keyword')
        category = request.query_params.get('category')

        events = get_events(category=category, keyword=search_keyword, type=self.model)
        result_page = paginator.paginate_queryset(queryset=events, request=request)
        serializer = self.serializer_class(result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return Response(response.data, status=status.HTTP_200_OK)


class OneTimeEventAPIView(EventAPIView):
    serializer_class = OneTimeEventSerializer
    model = OneTimeEvent


class RegularEventAPIView(EventAPIView):
    serializer_class = RegularEventSerializer
    model = RegularEvent


class CategoryAPIView(APIView):
    serializer_class = CategorySerializer
    model = Category

    @extend_schema(
        responses=CategorySerializer(many=True)
    )
    def get(self, request):
        categories = Category.objects.all()
        serializer = self.serializer_class(data=categories, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status.HTTP_200_OK)


class CommentCreateView(APIView):

    def post(self):
        serializer = EventCommentSerializer()

