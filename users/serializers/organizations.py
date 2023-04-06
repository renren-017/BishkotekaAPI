from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "user_id",
            "name",
            "type",
            "description",
            "address",
            "phone_number",
            "insta_link",
        )

    @staticmethod
    def get_user_id(obj) -> int:
        return obj.user.id


class OrganizationDetailSerializer(OrganizationSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "user_id",
            "name",
            "type",
            "description",
            "address",
            "phone_number",
            "insta_link",
        )


class OrganizationCreatedSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("user", "name")

    @staticmethod
    def get_user(obj) -> str:
        return obj.user.email


class OrganizationSignUpSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=1500)
    type = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(
        max_length=20, allow_blank=True, allow_null=True
    )
    address = serializers.CharField(max_length=200, allow_blank=True, allow_null=True)
    insta_link = serializers.URLField(allow_blank=True, allow_null=True)

    def create(self, validated_data):
        User = get_user_model()
        user = User.objects.get(id=validated_data["user_id"])
        organization = Organization.objects.create(
            user=user,
            name=validated_data["name"],
            description=validated_data["description"],
            type=validated_data["type"],
            phone_number=validated_data["phone_number"],
            address=validated_data["address"],
            insta_link=validated_data["insta_link"],
        )
        return organization
