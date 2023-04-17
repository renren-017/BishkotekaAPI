from rest_framework.permissions import BasePermission


class IsOrganizationOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True

        return obj.user == request.user


class IsProfileOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return view.kwargs["pk"] == request.user.pk


class IsProfileOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        return view.kwargs["pk"] == request.user.pk
