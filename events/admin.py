from django.contrib import admin
from events.models import Event, OneTimeEvent, RegularEvent, EventCategory, EventComment, EventInterest, EventPromotion, PromotionType, Category, OccurrenceDays
from django import forms


# class OccurrenceDaysInline(admin.TabularInline):
#     model = OccurrenceDays
#     max_num = 1
#     can_delete = False
#
#
# class CategoryInline(admin.TabularInline):
#     model = EventCategory
#
#
# class EventAdminForm(forms.ModelForm):
#     categories = forms.ModelMultipleChoiceField(
#         queryset=Category.objects.all(),
#         required=False,
#         widget=admin.widgets.FilteredSelectMultiple('categories', False),
#     )
#
#     class Meta:
#         model = Event
#         fields = '__all__'
#
#
# class EventAdmin(admin.ModelAdmin):
#     form = EventAdminForm
#     inlines = [OccurrenceDaysInline, CategoryInline]
#
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         obj.categories.clear()
#         for category in form.cleaned_data['categories']:
#             EventCategory.objects.create(event=obj, category=category)

admin.site.register(OccurrenceDays)
admin.site.register(Category)
admin.site.register(PromotionType)
admin.site.register(Event)
admin.site.register(OneTimeEvent)
admin.site.register(RegularEvent)
admin.site.register(EventPromotion)
admin.site.register(EventInterest)
admin.site.register(EventComment)
admin.site.register(EventCategory)
