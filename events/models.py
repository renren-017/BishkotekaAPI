from django.db import models
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField

from users.models import Organization, CustomUser


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class OccurrenceDays(models.Model):
    monday = models.BooleanField("понедельник", default=False)
    tuesday = models.BooleanField("вторник", default=False)
    wednesday = models.BooleanField("среда", default=False)
    thursday = models.BooleanField("четверг", default=False)
    friday = models.BooleanField("пятница", default=False)
    saturday = models.BooleanField("суббота", default=False)
    sunday = models.BooleanField("воскресенье", default=False)

    def __str__(self):
        days = []
        for day in [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]:
            if getattr(self, day):
                days.append(getattr(self._meta.get_field(day), "verbose_name"))
        return ", ".join(days)


ENTRY_TYPE_CHOICES = (
    ("свободный", "Свободный"),
    ("по приглашению", "По приглашению"),
    ("по регистрации", "По регистрации"),
)

MODERATION_STATUS_CHOICES = (
    ("отменён", "Отменён"),
    ("на модерации", "На модерации"),
    ("модерация пройдена", "Модерация пройдена"),
)


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    price = models.PositiveIntegerField()
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="events"
    )
    location = models.CharField(max_length=200)
    entry = models.CharField(
        choices=ENTRY_TYPE_CHOICES, max_length=15, default="свободный"
    )
    moderation_status = models.CharField(
        choices=MODERATION_STATUS_CHOICES, max_length=20, default="на модерации"
    )

    def __str__(self):
        return self.title


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images/")


class OneTimeEvent(Event):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class RegularEvent(Event):
    occurrence_days = models.ForeignKey(
        OccurrenceDays,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="events",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()


class EventCategory(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="categories"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="events"
    )

    def __str__(self):
        return f"{self.event.id} - {self.category.title}"


class EventComment(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text


class EventInterest(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="interests"
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="interested"
    )

    def __str__(self):
        return f"{self.user.id} - {self.event.id}"


class PromotionType(models.Model):
    title = models.CharField(max_length=100)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class EventPromotion(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="promotions"
    )
    promotion = models.ForeignKey(
        PromotionType, on_delete=models.CASCADE, related_name="events"
    )

    def __str__(self):
        return f"{self.event.id} - {self.promotion.id}"
