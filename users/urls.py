from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CustomerSignUpView, OrganizationSignUpView, SendVerificationEmailView, VerifyEmailView, \
    CustomerProfileView, OrganizationProfileView, CustomerTokenObtainPairView, OrganizationTokenObtainPairView

urlpatterns = [
    path('signup/customer/', CustomerSignUpView.as_view(), name='customer-signup'),
    path('signup/organization/', OrganizationSignUpView.as_view(), name='organization-signup'),

    # path('email/get_verification_letter/', SendVerificationEmailView.as_view(), name='email-send'),
    # path('email/verify/', VerifyEmailView.as_view(), name='email-verify'),

    path('login/customer/', CustomerTokenObtainPairView.as_view(), name='customer-token-obtain'),
    path('login/organization/', OrganizationTokenObtainPairView.as_view(), name='organization-token-obtain'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    path('profile/customer/', CustomerProfileView.as_view(), name='customer-profile'),
    path('profile/organization/', OrganizationProfileView.as_view(), name='organization-profile')
]
