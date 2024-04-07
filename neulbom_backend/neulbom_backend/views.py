from foodApp.views import getBodyMenuData
from boardApp.views import getTrendArticles
from calendarApp.views import getWeekEvent
from userApp.models import CustomUser
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime


def getNowdate():
    return str(datetime.now().date()).replace("-", "")


class MainInfo(APIView):
    def get(self, request):
        return Response(
            data={
                "foodData": getBodyMenuData(getNowdate()),
                "articleData": getTrendArticles(),
                "eventData": getWeekEvent(),
                "requester": {"username": f"{request.user.username}"},
            }
        )
