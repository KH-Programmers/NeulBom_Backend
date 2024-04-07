from .models import *
from rest_framework import serializers


class eventSerializer(serializers.ModelSerializer):
    class Meta:
        model = eventModel
        fields = "__all__"
