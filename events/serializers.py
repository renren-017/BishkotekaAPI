from abc import ABC

from rest_framework import serializers
from events.models import OneTimeEvent, EventCategory, EventComment, EventInterest, EventPromotion, RegularEvent


class UnixTimestampField(serializers.Field, ABC):
    def to_representation(self, value):
        return int(value.timestamp())


class EventCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = EventComment
        fields = ('user', 'text')


class EventInterestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = EventInterest
        fields = ('user',)


class EventCategorySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = EventCategory
        fields = ('category',)

    def to_representation(self, instance):
        category = instance.category
        return {
            'title': category.title
        }


class EventPromotionSerializer(serializers.ModelSerializer):
    promotion = serializers.StringRelatedField()

    class Meta:
        model = EventPromotion
        fields = ('promotion',)


class OneTimeEventSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    comments = EventCommentSerializer(many=True, read_only=True)
    interested = EventInterestSerializer(many=True, read_only=True)
    promotions = EventPromotionSerializer(many=True, read_only=True)
    organization = serializers.StringRelatedField()
    start_time = UnixTimestampField()
    end_time = UnixTimestampField()

    class Meta:
        model = OneTimeEvent
        fields = ('id', 'moderation_status', 'title', 'description', 'price', 'organization', 'location', 'entry', 'start_time', 'end_time', 'categories', 'comments', 'interested', 'promotions')


class RegularEventSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    comments = EventCommentSerializer(many=True, read_only=True)
    interested = EventInterestSerializer(many=True, read_only=True)
    promotions = EventPromotionSerializer(many=True, read_only=True)
    organization = serializers.StringRelatedField()
    occurrence_days = serializers.StringRelatedField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = RegularEvent
        fields = ('id', 'moderation_status', 'title', 'description', 'price', 'organization', 'location', 'entry', 'occurrence_days', 'start_time', 'end_time', 'categories', 'comments', 'interested', 'promotions')

    @staticmethod
    def get_start_time(obj):
        return obj.start_time.strftime('%H:%M')

    @staticmethod
    def get_end_time(obj):
        return obj.end_time.strftime('%H:%M')
