from django.core.mail import send_mail
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model

from users.models import Customer, Organization
from users.serializers import CustomerSignUpSerializer, OrganizationSignUpSerializer, EmailVerificationSerializer, CustomerSerializer, OrganizationSerializer
from config import settings
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

User = get_user_model()


class CustomerSignUpView(APIView):
    @extend_schema(
        request=CustomerSignUpSerializer)
    def post(self, request):
        serializer = CustomerSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"email": user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationSignUpView(APIView):
    @extend_schema(
        request=OrganizationSignUpSerializer)
    def post(self, request):
        serializer = OrganizationSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"Details": f"Account for {user.name} successfully created. Check your email inbox to verify your account"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationEmailView(APIView):
    @extend_schema(
        request=EmailVerificationSerializer)
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"Details": "User with email not found."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({"Details": "User email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        verification_token = self._generate_verification_token(user)
        subject = "Verify your email address"
        message = f"Here's your activation token: {verification_token}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except:
            return Response({"Details": "Could not send verification email."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"Details": "Verification email sent."}, status=status.HTTP_400_BAD_REQUEST)

    def _generate_verification_token(self, user):
        verification_token = user.generate_verification_token()
        return verification_token


class VerifyEmailView(APIView):
    @extend_schema(parameters=[
        OpenApiParameter("verification_token", OpenApiTypes.STR, OpenApiParameter.QUERY)
    ])
    def post(self, request):
        verification_token = request.query_params.get('verification_token')
        user = User.objects.filter(verification_token=verification_token).first()

        if not user:
            return Response({"Details": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.verification_token = ""
        user.save()

        return Response({"Details": "Email verified."})


class CustomerProfileView(APIView):
    @extend_schema(responses=CustomerSerializer)
    def get(self, request, pk):
        try:
            customer = Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


class OrganizationProfileView(APIView):
    @extend_schema(responses=OrganizationSerializer)
    def get(self, request, pk):
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)
