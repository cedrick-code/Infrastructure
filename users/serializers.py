from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Citizen

User = get_user_model()


class CitizenRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    contact_number = serializers.CharField(max_length=20)
    address = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username is already taken."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email is already registered."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")
        contact_number = validated_data.pop("contact_number")
        address = validated_data.pop("address")

        user = User.objects.create_user(
            **validated_data,
            password=password,
            role="citizen"
        )

        Citizen.objects.create(
            user=user,
            contact_number=contact_number,
            address=address
        )

        return user

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_email = data["username_or_email"]
        password = data["password"]

        user = User.objects.filter(
            email=username_or_email
        ).first()

        if user is None:
            user = User.objects.filter(
                username=username_or_email
            ).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid username/email or password."
            )

        if user.role != "citizen":
            raise serializers.ValidationError(
                "This login is for citizens only."
            )

        data["user"] = user
        return data