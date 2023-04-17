from abc import ABC
from django.db import transaction
from datetime import datetime

from rest_framework import serializers
from events.models import (
    OneTimeEvent,
    EventCategory,
    EventComment,
    EventInterest,
    EventPromotion,
    RegularEvent,
    Category,
    PromotionType,
    EventImage,
    Event,
    OccurrenceDays,
)
from users.models import Organization


class UnixTimestampField(serializers.Field, ABC):
    def to_representation(self, value):
        return int(value.timestamp())

    def to_internal_value(self, value):
        try:
            timestamp = int(value)
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            self.fail("invalid")


class EventCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    event = serializers.StringRelatedField()

    class Meta:
        model = EventComment
        fields = ("username", "text", "event")

    def create(self, validated_data):
        if validated_data["event"].moderation_status != "модерация пройдена":
            raise serializers.ValidationError(
                {
                    "Detail": "You are trying to comment on an event "
                    "that has not passed moderation yet"
                }
            )
        return super().create(validated_data)

    @staticmethod
    def get_username(obj):
        return obj.user.customer.username


class EventCommentInlineSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = EventComment
        fields = ("username", "text")

    @staticmethod
    def get_username(obj):
        return obj.user.customer.username


class EventInterestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = EventInterest
        fields = ("user",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title")


class EventCategorySerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    @staticmethod
    def get_id(obj) -> int:
        return obj.category.id

    class Meta:
        model = EventCategory
        fields = ("id",)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["title"] = instance.category.title
        return repr


class EventPromotionSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    @staticmethod
    def get_id(obj) -> int:
        return obj.promotion.id

    class Meta:
        model = EventPromotion
        fields = ("id",)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["title"] = instance.promotion.title
        return repr


class OneTimeEventSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    interested = EventInterestSerializer(many=True, read_only=True)
    promotions = EventPromotionSerializer(many=True, read_only=True)
    organization = serializers.StringRelatedField()
    start_time = UnixTimestampField()

    class Meta:
        model = OneTimeEvent
        fields = (
            "id",
            "title",
            "organization",
            "location",
            "start_time",
            "categories",
            "interested",
            "promotions",
        )


class OneTimeEventProfileSerializer(OneTimeEventSerializer):
    class Meta:
        model = OneTimeEvent
        fields = (
            "id",
            "title",
            "organization",
            "location",
            "start_time",
            "categories",
            "interested",
            "promotions",
            "moderation_status",
        )


class OneTimeEventDetailSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    comments = EventCommentInlineSerializer(many=True, read_only=True)
    interested = EventInterestSerializer(many=True, read_only=True)
    promotions = EventPromotionSerializer(many=True, read_only=True)
    organization = serializers.StringRelatedField()
    start_time = UnixTimestampField()
    end_time = UnixTimestampField()

    class Meta:
        model = OneTimeEvent
        fields = (
            "id",
            "title",
            "description",
            "price",
            "organization",
            "location",
            "entry",
            "start_time",
            "end_time",
            "categories",
            "comments",
            "interested",
            "promotions",
        )


class RegularEventSerializer(serializers.ModelSerializer):
    categories = EventCategorySerializer(many=True, read_only=True)
    interested = EventInterestSerializer(many=True, read_only=True)
    promotions = EventPromotionSerializer(many=True, read_only=True)
    organization = serializers.StringRelatedField()
    occurrence_days = serializers.StringRelatedField()
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = RegularEvent
        fields = (
            "id",
            "title",
            "organization",
            "location",
            "occurrence_days",
            "start_time",
            "categories",
            "interested",
            "promotions",
        )

    @staticmethod
    def get_start_time(obj):
        return obj.start_time.strftime("%H:%M")


class RegularEventProfileSerializer(RegularEventSerializer):
    class Meta:
        model = RegularEvent
        fields = (
            "id",
            "title",
            "organization",
            "location",
            "occurrence_days",
            "start_time",
            "categories",
            "interested",
            "promotions",
            "moderation_status",
        )


class RegularEventDetailSerializer(serializers.ModelSerializer):
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
        fields = (
            "id",
            "title",
            "description",
            "price",
            "organization",
            "location",
            "entry",
            "occurrence_days",
            "start_time",
            "end_time",
            "categories",
            "comments",
            "interested",
            "promotions",
        )

    @staticmethod
    def get_start_time(obj) -> int:
        return obj.start_time.strftime("%H:%M")

    @staticmethod
    def get_end_time(obj) -> int:
        return obj.end_time.strftime("%H:%M")


class EventImageInlineSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = EventImage
        fields = ("image",)


class CategoryInlineSerializer:
    class Meta:
        model = Category
        fields = ("title",)


class EventCreateSerializer(serializers.ModelSerializer):
    promotions = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        write_only=True,
    )
    categories = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    organization = serializers.HiddenField(default=None, allow_null=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "price",
            "location",
            "entry",
            "organization",
            "images",
            "categories",
            "promotions",
        )

    def validate_promotions(self, value):
        value = value[0].split(",")
        for prom in value:
            if not PromotionType.objects.filter(title=prom).exists():
                raise serializers.ValidationError(
                    {
                        "Detail": f"{prom} promotion type either is disabled or does not exist"
                    }
                )
        return value

    def validate_categories(self, value):
        value = value[0].split(",")
        for cat in value:
            if not Category.objects.filter(title=cat).exists():
                raise serializers.ValidationError(
                    {"Detail": f"{cat} is not an existing category"}
                )
        return value

    def create(self, validated_data):
        promotions_data = validated_data.pop("promotions", [])
        images_data = validated_data.pop("images", [])
        categories_data = validated_data.pop("categories", [])

        with transaction.atomic():
            event = self.Meta.model.objects.create(**validated_data)

            event_images = [
                EventImage(event=event, image=image_data) for image_data in images_data
            ]
            EventImage.objects.bulk_create(event_images)

            categories = []
            for category_data in categories_data:
                categories.append(Category.objects.get(title=category_data))
            event_categories = [
                EventCategory(event=event, category=category_data)
                for category_data in categories
            ]
            EventCategory.objects.bulk_create(event_categories)

            promotions = []
            for promotion_data in promotions_data:
                promotions.append(PromotionType.objects.get(title=promotion_data))

            event_promotions = [
                EventPromotion(event=event, promotion=promotion_data)
                for promotion_data in promotions
            ]
            EventPromotion.objects.bulk_create(event_promotions)

            return event

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["categories"] = [
            cat.category.title for cat in EventCategory.objects.filter(event=instance)
        ]
        repr["promotions"] = [
            cat.promotion.title for cat in EventPromotion.objects.filter(event=instance)
        ]
        repr["images"] = [
            cat.image.url for cat in EventImage.objects.filter(event=instance)
        ]
        return repr


class OneTimeEventCreateSerializer(EventCreateSerializer):
    start_time = UnixTimestampField()
    end_time = UnixTimestampField()

    class Meta:
        model = OneTimeEvent
        fields = (
            "id",
            "title",
            "description",
            "price",
            "location",
            "entry",
            "start_time",
            "end_time",
            "organization",
            "images",
            "categories",
            "promotions",
        )


class RegularEventCreateSerializer(EventCreateSerializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    occurrence_days = serializers.ListField(
        child=serializers.CharField(default="monday"), write_only=True
    )

    class Meta:
        model = RegularEvent
        fields = (
            "id",
            "title",
            "description",
            "price",
            "location",
            "entry",
            "start_time",
            "end_time",
            "organization",
            "images",
            "categories",
            "promotions",
            "occurrence_days",
        )

    def create(self, validated_data):
        validated_days = {
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }

        for key in validated_data["occurrence_days"][0].split(","):
            validated_days[key] = True

        occurrence_days, created = OccurrenceDays.objects.get_or_create(
            **validated_days
        )
        validated_data["occurrence_days"] = occurrence_days
        return super().create(validated_data)

    def to_representation(self, instance):
        print(instance.occurrence_days)
        repr = super().to_representation(instance)

        repr["occurrence_days"] = str(instance.occurrence_days).split(", ")
        return repr
