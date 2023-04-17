from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from events.models import Category
from events.serializers import CategorySerializer
from users.models import Customer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
        )


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    # interests = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
        )

    @staticmethod
    def get_email(obj) -> str:
        return obj.user.email

    @staticmethod
    def get_id(obj) -> int:
        return obj.user.id

    @staticmethod
    def get_interests(obj) -> dict:
        categories = Category.objects.filter(id__in=obj.interests_ids)
        return CategorySerializer(categories, many=True).data


class CustomerProfileSerializer(CustomerSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "following_count",
        )


class CustomerCreatedSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ("email", "username", "first_name", "last_name")

    @staticmethod
    def get_email(obj) -> str:
        return obj.user.email


class CustomerSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    # first_name = serializers.CharField()
    # last_name = serializers.CharField()
    # interests_ids = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            date_joined=timezone.now(),
        )
        user.is_active = True
        user.save()
        customer = Customer.objects.create(
            user=user,
            username=validated_data["username"],
        )
        return customer

    def validate_email(self, value):
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    class Meta:
        fields = ("username", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"] = serializers.CharField()
        self.fields["password"] = serializers.CharField(
            style={"input_type": "password"}, trim_whitespace=False
        )
        del self.fields["email"]

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        # Authenticate the user based on the username field
        user = Customer.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError("User not found")

        user = user.user
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        refresh = self.get_token(user)

        data = {"refresh": str(refresh), "access": str(refresh.access_token), "id": user.id}

        return data
