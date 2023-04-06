from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from users.views import (
    CustomerSignUpView,
    OrganizationSignUpView,
    SendVerificationEmailView,
    VerifyEmailView,
    CustomerProfileView,
    OrganizationProfileView,
    CustomerTokenObtainPairView,
    PasswordResetConfirmView,
    PasswordResetView,
    OrganizationProfileDetailView,
)

urlpatterns = [
    path(
        "users/signup/customer/", CustomerSignUpView.as_view(), name="customer-signup"
    ),
    path(
        "users/create/organization/",
        OrganizationSignUpView.as_view(),
        name="organization-signup",
    ),
    # path('users/email/get_verification_letter/', SendVerificationEmailView.as_view(), name='email-send'),
    # path('email/verify/', VerifyEmailView.as_view(), name='email-verify'),
    path("users/password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "users/password_reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "users/login/",
        CustomerTokenObtainPairView.as_view(),
        name="customer-token-obtain",
    ),
    path("users/login/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # path("profile/customer/", CustomerProfileView.as_view(), name="customer-profile"),
    path(
        "profile/organizations/",
        OrganizationProfileView.as_view(),
        name="organization-profile",
    ),
    path(
        "profile/organization/<int:pk>",
        OrganizationProfileDetailView.as_view(),
        name="organization-profile",
    )
]
