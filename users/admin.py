from django.contrib import admin
from users.models import CustomUser, Customer, Organization


class UserAdmin(admin.ModelAdmin):
    icon_name = "perm_identity"
    list_display = ("id", "email", "is_active", "date_joined", "profile_type")

    def profile_type(self, obj):
        if hasattr(obj, "customer"):
            return "Customer"
        if hasattr(obj, "organization"):
            return "Organization"
        if obj.is_staff:
            return "Staff member"
        else:
            return "Not figured"

    profile_type.short_description = "Profile Type"


admin.site.register(CustomUser, UserAdmin)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    icon_name = "person"
    list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    icon_name = "group"
    list_display = ("id", "user", "name", "type", "following_count")
