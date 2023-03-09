from django.urls import path
from users.views import CustomerSignUpView, OrganizationSignUpView, SendVerificationEmailView, VerifyEmailView, \
    CustomerProfileView, OrganizationProfileView

urlpatterns = [
    path('signup/user/', CustomerSignUpView.as_view(), name='customer-signup'),
    path('signup/organization/', OrganizationSignUpView.as_view(), name='organization-signup'),
    path('email/get_verification_letter/', SendVerificationEmailView.as_view(), name='email-send'),
    path('email/verify/', VerifyEmailView.as_view(), name='email-verify'),

    path('profile/customer/<int:pk>/', CustomerProfileView.as_view(), name='customer-profile'),
    path('profile/organization/<int:pk>/', OrganizationProfileView.as_view(), name='organization-profile')
]
