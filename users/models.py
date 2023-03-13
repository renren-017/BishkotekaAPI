from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email_address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    verification_token = models.CharField(max_length=150, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.customer.username if hasattr(self, 'customer') else self.organization.name

    def generate_verification_token(self):
        token = make_password(f"{self.email}-{self.date_joined}")
        self.verification_token = token
        self.save()

        return token


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    username = models.CharField(_("username"), max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    interests_ids = ArrayField(models.IntegerField(), blank=True)

    def __str__(self):
        return self.username


class Organization(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1500)
    type = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200)
    insta_link = models.URLField()

    def __str__(self):
        return self.name


class Following(models.Model):
    follower = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name="followers")
