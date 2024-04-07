from .models import CustomUser as User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from turnstile.fields import TurnstileField
import base64
from django.conf import settings
from .models import CustomUser
from drf_extra_fields.fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "email", "grade", "school", "is_allowed", "card_img"]
        reqd_only_fields = ["last_login", "date_joined"]


# 로그인
class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), username=username, password=password
        )
        if not user:
            msg = "Unable to authenticate with provided credentials"
            raise serializers.ValidationError(msg, code="authentication")
        attrs["user"] = user
        return attrs["user"]


# 회원가입
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    card_img = Base64ImageField()

    class Meta:
        model = User
        fields = ("username", "name", "email", "password", "grade", "card_img")
        extra_kwargs = {}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            name=validated_data["name"],
            email=validated_data["email"],
            grade=validated_data["grade"],
            card_img=validated_data["card_img"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
