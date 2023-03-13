from django.contrib import admin
from users.models import CustomUser, Customer, Organization


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'is_active', 'date_joined', 'profile_type')

    def profile_type(self, obj):
        if hasattr(obj, 'customer'):
            return 'Customer'
        if hasattr(obj, 'organization'):
            return 'Organization'
        if obj.is_staff:
            return 'Staff member'
        else:
            return 'Not figured'

    profile_type.short_description = 'Profile Type'


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Customer)
admin.site.register(Organization)
