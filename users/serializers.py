# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Customer, Organization


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email',)


class CustomerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Customer
        fields = ('username', 'first_name', 'last_name', 'date_of_birth', 'user')


class OrganizationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('name', 'description', 'type', 'user')

    def get_type(self, obj):
        return obj.type.name


class CustomerSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    interests_ids = serializers.ListField()

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            date_joined=timezone.now()
        )
        user.is_active = False
        user.save()
        customer = Customer.objects.create(
            user=user,
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            date_of_birth=validated_data['date_of_birth'],
            interests_ids=validated_data['interests_ids']
        )
        return user

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords do not match')
        return attrs


class OrganizationSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1500)
    type = serializers.CharField(max_length=100)

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            date_joined=timezone.now()
        )
        user.is_active = False
        user.save()
        organization = Organization.objects.create(
            user=user,
            name=validated_data['name'],
            description=validated_data['description'],
            type=validated_data['type'],
        )
        return organization

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords do not match')
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
