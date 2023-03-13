from django.urls import path
from events.views import OneTimeEventAPIView, RegularEventAPIView

urlpatterns = [
    path('onetime', OneTimeEventAPIView.as_view(), name='onetime-events'),
    path('regular', RegularEventAPIView.as_view(), name='regular-events')
]