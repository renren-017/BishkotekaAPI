from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from users.models import Organization


class IsOwnerOrDenied(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        org_name = view.kwargs.get("name")
        organization = get_object_or_404(Organization, name=org_name)
        return organization.user == request.user
