from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Customer, Organization
from users.serializers import CustomerSignUpSerializer, OrganizationSignUpSerializer, EmailVerificationSerializer, \
    CustomerSerializer, OrganizationSerializer, CustomerTokenObtainPairSerializer, \
    OrganizationTokenObtainPairSerializer, OrganizationCreatedSerializer, CustomerCreatedSerializer, \
    PasswordResetConfirmSerializer, PasswordResetSerializer
from config import settings
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

User = get_user_model()


class CustomerSignUpView(APIView):
    @extend_schema(
        request=CustomerSignUpSerializer,
        responses=CustomerCreatedSerializer)
    def post(self, request):
        serializer = CustomerSignUpSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({"email": customer.user.email,
                             "username": customer.username,
                             "first_name": customer.first_name,
                             "last_name": customer.last_name},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationSignUpView(APIView):
    @extend_schema(
        request=OrganizationSignUpSerializer,
        responses=OrganizationCreatedSerializer)
    def post(self, request):
        serializer = OrganizationSignUpSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save(user_id=request.user.id)
            return Response({"user": organization.user.email,
                             "organization_name": organization.name},
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
    def get(self, request):
        try:
            customer = Customer.objects.get(pk=request.user.id)
        except Customer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


class OrganizationProfileView(APIView):
    @extend_schema(responses=OrganizationSerializer)
    def get(self, request):
        try:
            organization = Organization.objects.get(pk=request.user.id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)


class CustomerTokenObtainPairView(TokenObtainPairView):
    @extend_schema(request=CustomerTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        if 'username' in request.data:
            request_serializer = CustomerTokenObtainPairSerializer(data=request.data)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        if request_serializer.is_valid():
            token_data = request_serializer.validated_data
            return Response(token_data, status=status.HTTP_200_OK)

        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationTokenObtainPairView(TokenObtainPairView):
    @extend_schema(request=OrganizationTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        if 'name' in request.data:
            request_serializer = OrganizationTokenObtainPairSerializer(data=request.data)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        if request_serializer.is_valid():
            token_data = request_serializer.validated_data
            return Response(token_data, status=status.HTTP_200_OK)

        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token_generator = default_token_generator
        reset_url = f'{request.scheme}://{request.get_host()}/api/password_reset/confirm/?uidb64={uidb64}&token={token_generator.make_token(user)}'
        subject = 'Password reset for your account'
        html_message = render_to_string('email/password_reset_email.html', {
            'user': user.email,
            'reset_url': reset_url,
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        email = EmailMultiAlternatives(
            subject,
            plain_message,
            from_email,
            recipient_list,
        )

        email.content_subtype = "html"
        email.attach_alternative(html_message, 'text/html')
        email.send()

        return Response({'detail': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password1 = serializer.validated_data['new_password1']
        new_password2 = serializer.validated_data['new_password2']

        try:
            uid = int(urlsafe_base64_decode(uidb64).decode('utf-8'))
            user = User.objects.get(pk=uid)
            token_generator = default_token_generator
            if not token_generator.check_token(user, token):
                raise ObjectDoesNotExist
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist, ValidationError):
            return Response({'detail': 'Invalid password reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        form = SetPasswordForm(user, {'new_password1': new_password1, 'new_password2': new_password2})
        if form.is_valid():
            form.save()
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Something went form with the form, try again.'}, status=status.HTTP_400_BAD_REQUEST)