from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.http import Http404
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from config import settings
from users.models import Customer
from users.permissions import IsProfileOwnerOrReadOnly
from users.serializers.passwords import (
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from users.serializers.users import (
    CustomerSignUpSerializer,
    CustomerCreatedSerializer,
    EmailVerificationSerializer,
    CustomerSerializer,
    CustomerTokenObtainPairSerializer, CustomerProfileSerializer,
)


User = get_user_model()


class CustomerSignUpView(APIView):
    @extend_schema(
        request=CustomerSignUpSerializer, responses=CustomerCreatedSerializer
    )
    def post(self, request):
        serializer = CustomerSignUpSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                {
                    "email": customer.user.email,
                    "username": customer.username,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationEmailView(APIView):
    @extend_schema(request=EmailVerificationSerializer)
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            return Response(
                {"Details": "User with email not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"Details": "User email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        verification_token = self._generate_verification_token(user)
        subject = "Verify your email address"
        message = f"Here's your activation token: {verification_token}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except:
            return Response(
                {"Details": "Could not send verification email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"Details": "Verification email sent."}, status=status.HTTP_400_BAD_REQUEST
        )

    def _generate_verification_token(self, user):
        verification_token = user.generate_verification_token()
        return verification_token


class VerifyEmailView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "verification_token", OpenApiTypes.STR, OpenApiParameter.QUERY
            )
        ]
    )
    def post(self, request):
        verification_token = request.query_params.get("verification_token")
        user = User.objects.filter(verification_token=verification_token).first()

        if not user:
            return Response(
                {"Details": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.verification_token = ""
        user.save()

        return Response({"Details": "Email verified."})


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]

    def get_object(self):
        customer = Customer.objects.filter(user=self.kwargs['pk'])

        if not customer:
            raise Http404("No active customer profile with this pk found")
        return customer.first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.get_object())
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CustomerTokenObtainPairView(TokenObtainPairView):
    @extend_schema(request=CustomerTokenObtainPairSerializer)
    def post(self, request, *args, **kwargs):
        if "username" in request.data:
            request_serializer = CustomerTokenObtainPairSerializer(data=request.data)
        else:
            return Response(
                {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )

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
        reset_url = f"{request.scheme}://{request.get_host()}/api/password_reset/confirm/?uidb64={uidb64}&token={token_generator.make_token(user)}"
        subject = "Password reset for your account"
        html_message = render_to_string(
            "email/password_reset_email.html",
            {
                "user": user.email,
                "reset_url": reset_url,
            },
        )
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
        email.attach_alternative(html_message, "text/html")
        email.send()

        return Response(
            {"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password1 = serializer.validated_data["new_password1"]
        new_password2 = serializer.validated_data["new_password2"]
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]

        try:
            uid = int(urlsafe_base64_decode(uidb64).decode("utf-8"))
            user = User.objects.get(pk=uid)
            token_generator = default_token_generator
            if not token_generator.check_token(user, token):
                raise ObjectDoesNotExist
        except (
            TypeError,
            ValueError,
            OverflowError,
            ObjectDoesNotExist,
            ValidationError,
        ):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = SetPasswordForm(
            user, {"new_password1": new_password1, "new_password2": new_password2}
        )
        if form.is_valid():
            form.save()
            return Response(
                {"detail": "Password has been reset."}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Something went form with the form, try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )
