from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from events.models import OneTimeEvent, RegularEvent
from events.serializers import OneTimeEventSerializer, RegularEventSerializer


class OneTimeEventAPIView(APIView):
    @extend_schema(
        responses=OneTimeEventSerializer)
    def get(self, request):
        events = OneTimeEvent.objects.all()
        serializer = OneTimeEventSerializer(events, many=True)
        return Response(serializer.data)


class RegularEventAPIView(APIView):
    @extend_schema(
        responses=RegularEventSerializer)
    def get(self, request):
        events = RegularEvent.objects.all()
        serializer = RegularEventSerializer(events, many=True)
        return Response(serializer.data)
