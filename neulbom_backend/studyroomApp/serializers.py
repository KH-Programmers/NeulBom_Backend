from rest_framework import serializers
from userApp.models import CustomUser
from .models import seatModel

class userSerializer(serializers.Serializer):
    class Meta:
        model = CustomUser
        fields = (
            "name",
            "grade",
            )

class seatSerializer(serializers.Serializer):
    class Meta:
        model = seatModel
        fields = (
            "roomNum",
            "seatNum"
        )