import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework import viewsets, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from events.models import (
    OneTimeEvent,
    RegularEvent,
    Category,
    EventComment,
    EventPromotion,
    EventCategory,
    EventImage,
    Event, EventInterest,
)
from events.permissions import IsOwnerOrDenied
from events.serializers import (
    OneTimeEventSerializer,
    RegularEventSerializer,
    EventCommentSerializer,
    OneTimeEventDetailSerializer,
    RegularEventDetailSerializer,
    CategorySerializer,
    OneTimeEventCreateSerializer,
    RegularEventCreateSerializer,
)
from users.models import Organization
from utils.db.queries import get_events, get_categories


class EventAPIView(APIView):
    serializer_class = OneTimeEventSerializer
    pagination_class = LimitOffsetPagination
    model = OneTimeEvent

    @extend_schema(
        responses=serializer_class(many=True),
        parameters=[
            OpenApiParameter(name="limit", type=int),
            OpenApiParameter(name="offset", type=int),
            OpenApiParameter(name="keyword", type=str),
            OpenApiParameter(name="category", type=int),
        ],
    )
    def get(self, request):
        self.check_permissions(request)
        paginator = self.pagination_class()
        search_keyword = request.query_params.get("keyword")
        category = request.query_params.get("category")

        events = get_events(category=category, keyword=search_keyword, type=self.model)
        result_page = paginator.paginate_queryset(queryset=events, request=request)
        serializer = self.serializer_class(result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return Response(response.data, status=status.HTTP_200_OK)


class OneTimeEventAPIView(EventAPIView):
    serializer_class = OneTimeEventSerializer
    queryset = OneTimeEvent.objects.filter(moderation_status="модерация пройдена")

    @extend_schema(
        responses=serializer_class(many=True),
        parameters=[
            OpenApiParameter(name="keyword", type=str),
            OpenApiParameter(name="category", type=int),
            OpenApiParameter(name="start_time", type=int),
        ],
    )
    def get(self, request):
        self.check_permissions(request)
        paginator = self.pagination_class()
        search_keyword = request.query_params.get("keyword")
        category = request.query_params.get("category")
        start_time = request.query_params.get("start_time")

        events = get_events(
            category=category,
            keyword=search_keyword,
            start_time=start_time,
            type=self.model,
        )
        result_page = paginator.paginate_queryset(queryset=events, request=request)
        serializer = self.serializer_class(result_page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        return Response(response.data, status=status.HTTP_200_OK)


class RegularEventAPIView(EventAPIView):
    serializer_class = RegularEventSerializer
    queryset = RegularEvent.objects.filter(moderation_status="модерация пройдена")
    model = RegularEvent


class CategoryAPIView(APIView):
    serializer_class = CategorySerializer
    model = Category

    @extend_schema(
        responses=CategorySerializer(many=True),
        parameters=[
            OpenApiParameter(name="is_not_empty", type=bool),
        ],
    )
    def get(self, request):
        is_not_empty = request.query_params.get("is_not_empty")
        categories = get_categories(is_not_empty)
        serializer = self.serializer_class(data=categories, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status.HTTP_200_OK)


class OneTimeEventDetailView(RetrieveAPIView):
    serializer_class = OneTimeEventDetailSerializer
    queryset = OneTimeEvent.objects.all()
    lookup_url_kwarg = "pk"


class RegularEventDetailView(RetrieveAPIView):
    serializer_class = RegularEventDetailSerializer
    queryset = RegularEvent.objects.all()
    lookup_url_kwarg = "pk"


class EventCommentCreateAPIView(CreateAPIView):
    serializer_class = EventCommentSerializer
    queryset = EventComment.objects.all()
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        event = Event.objects.get(id=self.kwargs.get("pk"))
        serializer.save(user=self.request.user, event=event)


class EventCreateView(CreateAPIView):
    serializer_class = OneTimeEventCreateSerializer
    queryset = OneTimeEvent.objects.all()
    parser_classes = (MultiPartParser,)
    permission_classes = (IsOwnerOrDenied,)

    @extend_schema(request=OneTimeEventCreateSerializer)
    def post(self, request, *args, **kwargs):
        request.data._mutable = True

        if request.data["images"] == "":
            del request.data["images"]

        if request.data["promotions"] == "":
            del request.data["promotions"]

        if request.data["categories"] == "":
            del request.data["categories"]

        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(organization=Organization.objects.get(id=self.kwargs.get("pk")))


class OneTimeEventCreateView(EventCreateView):
    serializer_class = OneTimeEventCreateSerializer
    queryset = OneTimeEvent.objects.all()
    parser_classes = (MultiPartParser,)
    permission_classes = (IsOwnerOrDenied,)

    @extend_schema(request=OneTimeEventCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegularEventCreateView(EventCreateView):
    serializer_class = RegularEventCreateSerializer
    queryset = RegularEvent.objects.all()
    parser_classes = (MultiPartParser,)
    permission_classes = (IsOwnerOrDenied,)

    @extend_schema(request=RegularEventCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class EventFavouriteView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, pk):
        self.check_permissions(request)
        user = request.user

        if not pk:
            return Response(
                {"Detail": "interest_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event = Event.objects.filter(id=pk)
        if not event:
            return Response(
                {
                    "Detail": "The event with the given event_id does not exist."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if EventInterest.objects.filter(
            user=user, event=event.first()
        ).exists():
            EventInterest.objects.filter(
                user=user, event=event.first()
            ).delete()
            return Response(
                {"Detail": "You have unstarred this event."},
                status=status.HTTP_200_OK,
            )

        EventInterest.objects.create(
            user=user, event=event.first()
        )
        return Response(
            {"Detail": "You have starred event."},
            status=status.HTTP_201_CREATED,
        )