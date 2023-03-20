from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from events.models import Category
from events.serializers import CategorySerializer
from users.models import Customer, Organization


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email',)


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_of_birth', 'interests')

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


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('id', 'email', 'name', 'type', 'description', 'address', 'phone_number', 'insta_link')

    @staticmethod
    def get_email(obj) -> str:
        return obj.user.email

    @staticmethod
    def get_id(obj) -> int:
        return obj.user.id


class OrganizationCreatedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('user', 'name')

    @staticmethod
    def get_user(obj) -> str:
        return obj.user.email


class CustomerCreatedSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ('email', 'username', 'first_name', 'last_name')

    @staticmethod
    def get_email(obj) -> str:
        return obj.user.email


class CustomerSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_of_birth = serializers.DateField()
    interests_ids = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            date_joined=timezone.now()
        )
        user.is_active = True
        user.save()
        customer = Customer.objects.create(
            user=user,
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            date_of_birth=validated_data['date_of_birth'],
            interests_ids=validated_data['interests_ids']
        )
        return customer

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
    user_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1500)
    type = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20, allow_blank=True, allow_null=True)
    address = serializers.CharField(max_length=200, allow_blank=True, allow_null=True)
    insta_link = serializers.URLField(allow_blank=True, allow_null=True)

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.get(id=validated_data['user_id'])
        organization = Organization.objects.create(
            user=user,
            name=validated_data['name'],
            description=validated_data['description'],
            type=validated_data['type'],
            phone_number=validated_data['phone_number'],
            address=validated_data['address'],
            insta_link=validated_data['insta_link']
        )
        return organization


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):
    class Meta:
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'] = serializers.CharField()
        self.fields['password'] = serializers.CharField(
            style={'input_type': 'password'},
            trim_whitespace=False
        )
        del self.fields['email']

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Authenticate the user based on the username field
        user = Customer.objects.filter(username=username).first()
        if not user:
            raise serializers.ValidationError('User not found')

        user = user.user
        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

        return data


class OrganizationTokenObtainPairSerializer(TokenObtainPairSerializer):
    class Meta:
        fields = ('name', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'] = serializers.CharField()
        self.fields['password'] = serializers.CharField(
            style={'input_type': 'password'},
            trim_whitespace=False
        )
        del self.fields['email']

    def validate(self, attrs):
        name = attrs.get('name')
        password = attrs.get('password')

        # Authenticate the user based on the name field
        user = Organization.objects.filter(name=name).first()
        if not user:
            raise serializers.ValidationError('User not found')

        user = user.user

        if not user.check_password(password):
            raise serializers.ValidationError('Incorrect password')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')

        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

        return data
