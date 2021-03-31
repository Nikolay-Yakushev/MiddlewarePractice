from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from typing import ClassVar

from backend_users.middleware import IpCheckMiddleware


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user


class AuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    # token = serializers.JSONField()


class ShowAllUsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "password"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
        ]


class UnbanSubnetSerializer(serializers.Serializer):
    subnet_to_unban = serializers.IPAddressField()

    def validate(self, attrs):
        validators = [
            self.check_ip_banned,

        ]

        for validator in validators:
            validator(attrs)
        return attrs

    def check_ip_banned(self, attrs):
        if attrs["subnet_to_unban"] not in IpCheckMiddleware.banned_subnet:
            raise serializers.ValidationError("Subnet is not banned")
        return attrs
