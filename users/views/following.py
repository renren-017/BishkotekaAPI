from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiParameter

from users.models import FollowingOrganization, Organization, Following

User = get_user_model()


class FollowingOrganizationView(APIView):
    # @extend_schema(parameters=[OpenApiParameter(name="following_id", type=int)])
    def post(self, request, pk):
        follower = request.user

        if not pk:
            return Response(
                {"Detail": "following_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        following = Organization.objects.filter(id=pk)
        if not following:
            return Response(
                {
                    "Detail": "The organization with the given following_id does not exist."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if FollowingOrganization.objects.filter(
            follower=follower, following=following.first()
        ).exists():
            FollowingOrganization.objects.filter(
                follower=follower, following=following.first()
            ).delete()
            return Response(
                {"Detail": "You have unfollowed this organization."},
                status=status.HTTP_200_OK,
            )

        FollowingOrganization.objects.create(
            follower=follower, following=following.first()
        )
        return Response(
            {"Detail": "You are now following this organization."},
            status=status.HTTP_201_CREATED,
        )


class FollowingView(APIView):
    def post(self, request, pk):
        follower = request.user

        if not pk:
            return Response(
                {"Detail": "following_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if follower.pk == pk:
            return Response(
                {"Detail": "Customers cannot follow themselves"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        following = User.objects.filter(id=pk)
        if not following:
            return Response(
                {"Detail": "The user with the given pk does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Following.objects.filter(
            follower=follower, following=following.first()
        ).exists():
            Following.objects.filter(
                follower=follower, following=following.first()
            ).delete()
            return Response(
                {"Detail": "You have unfollowed this user."}, status=status.HTTP_200_OK
            )

        Following.objects.create(follower=follower, following=following.first())
        return Response(
            {"Detail": "You are now following this user."},
            status=status.HTTP_201_CREATED,
        )
