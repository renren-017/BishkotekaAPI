from django.contrib import admin
from events.models import (
    Event,
    OneTimeEvent,
    RegularEvent,
    EventCategory,
    EventComment,
    EventInterest,
    EventPromotion,
    PromotionType,
    Category,
    OccurrenceDays,
)
from django import forms


@admin.register(OccurrenceDays)
class OccurrenceDaysAdmin(admin.ModelAdmin):
    icon_name = "event_available"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    icon_name = "event"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(OneTimeEvent)
class OneTimeEventAdmin(admin.ModelAdmin):
    icon_name = "radio_button_checked"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(RegularEvent)
class RegularEventAdmin(admin.ModelAdmin):
    icon_name = "query_builder"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(EventPromotion)
class EventPromotionAdmin(admin.ModelAdmin):
    icon_name = "trending_up"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(EventInterest)
class EventInterestAdmin(admin.ModelAdmin):
    icon_name = "thumb_up"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    icon_name = "comment"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    icon_name = "widgets"
    # list_display = ("user", "username", "first_name", "last_name", "following_count")
