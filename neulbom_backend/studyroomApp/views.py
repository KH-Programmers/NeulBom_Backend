from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import seatModel
from .serializers import *

class studyroom(APIView):
    def get(self, request):
        return Response(userSerializer(request.user).data)
    def post(self, request):
        serializer = seatSerializer(data=request.data)
        if serializer.is_valid():
            if seatModel.objects.filter(user=request.user):
                return Response({"error": "이미 좌석을 예매했습니다."}, status=status.HTTP_409_CONFLICT)
            if seatModel.objects.filter(seatNum=request.data.get("seatNum"),roomNum=request.data.get("roomNum")):
                return Response({"error": "이미 예매된 좌석입니다."}, status=status.HTTP_409_CONFLICT)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
