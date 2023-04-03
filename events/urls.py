from django.urls import path
from events.views import (
    OneTimeEventAPIView,
    RegularEventAPIView,
    CategoryAPIView,
    EventCommentCreateAPIView,
    OneTimeEventDetailView,
    RegularEventDetailView,
    OneTimeEventCreateView,
    RegularEventCreateView,
)

urlpatterns = [
    path("events/onetime/", OneTimeEventAPIView.as_view(), name="onetime-events"),
    path(
        "events/onetime/<int:pk>",
        OneTimeEventDetailView.as_view(),
        name="onetime-events-detail",
    ),
    path("events/regular/", RegularEventAPIView.as_view(), name="regular-events"),
    path(
        "events/regular/<int:pk>",
        RegularEventDetailView.as_view(),
        name="regular-events-detail",
    ),
    path("events/categories/", CategoryAPIView.as_view(), name="categories"),
    path(
        "events/<int:pk>/comment/",
        EventCommentCreateAPIView.as_view(),
        name="comment-create",
    ),
    path(
        "organization/<int:pk>/events/onetime/create/", OneTimeEventCreateView.as_view()
    ),
    path(
        "organization/<int:pk>/events/regular/create/", RegularEventCreateView.as_view()
    ),
]
