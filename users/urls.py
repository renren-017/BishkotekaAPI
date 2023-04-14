from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from users.views.customers import (
    CustomerSignUpView,
    PasswordResetView,
    PasswordResetConfirmView,
    CustomerTokenObtainPairView,
    CustomerProfileView,
)
from users.views.following import FollowingOrganizationView, FollowingView
from users.views.organizations import (
    OrganizationSignUpView,
    OrganizationProfileView,
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
    path(
        "profile/customer/<int:pk>/",
        CustomerProfileView.as_view(),
        name="customer-profile",
    ),
    path(
        "profile/customer/<int:pk>/organizations/",
        OrganizationProfileView.as_view(),
        name="organization-profile",
    ),
    path(
        "profile/organization/<int:pk>/",
        OrganizationProfileDetailView.as_view(),
        name="organization-profile",
    ),
    path(
        "accounts/organization/<int:pk>/follow/",
        FollowingOrganizationView.as_view(),
        name="organization-follow",
    ),
    path(
        "accounts/customer/<int:pk>/follow/",
        FollowingView.as_view(),
        name="customer-follow",
    ),
]
