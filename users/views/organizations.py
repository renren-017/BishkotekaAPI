from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Organization
from users.permissions import IsOrganizationOwnerOrReadOnly, IsProfileOwnerOrReadOnly, IsProfileOwner
from users.serializers.organizations import (
    OrganizationSignUpSerializer,
    OrganizationCreatedSerializer,
    OrganizationSerializer, OrganizationProfileSerializer,
)

User = get_user_model()


class OrganizationSignUpView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=OrganizationSignUpSerializer, responses=OrganizationCreatedSerializer
    )
    def post(self, request):
        self.check_permissions(request)
        serializer = OrganizationSignUpSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save(user_id=request.user.id)
            return Response(
                {
                    "user": organization.user.email,
                    "organization_name": organization.name,
                    "organization_id": organization.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationProfileView(generics.ListAPIView):
    permission_classes = (IsProfileOwner,)
    serializer_class = OrganizationProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return Organization.objects.filter(user=self.kwargs.get('pk'))


class OrganizationProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOrganizationOwnerOrReadOnly,)
    serializer_class = OrganizationSerializer
    lookup_url_kwarg = "pk"
    queryset = Organization.objects.all()
