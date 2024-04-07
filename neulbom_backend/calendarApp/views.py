from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
import datetime


def getMonthDates(month):
    if month == 2:
        year = datetime.now().year
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return 29
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return days[month - 1]


def geteventBody(date: str):
    try:
        serializer = eventSerializer(eventModel.objects.get(date=int(date))).data
    except:
        serializer = {"date": int(date), "eventName": None, "type": None}
    return serializer


def getWeekEvent():
    nowdate = datetime.datetime.now()
    sunday = nowdate - datetime.timedelta(days=(nowdate.weekday() + 1) % 7)
    yearmonth = f"{sunday.year}{0 if sunday.month < 10 else ''}{sunday.month}"
    day = sunday.day
    bodys = []
    for i in range(7):
        date = yearmonth + f"{0 if day<10 else ''}{day+i}"
        bodys.append(geteventBody(date))
    return bodys


class weekEventView(APIView):
    def get(self, request):
        data = getWeekEvent()
        return Response(data=data)


class monthEventView(APIView):
    def get(self, request, year, month):
        if not 1 <= month <= 12:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        body = []
        for i in range(getMonthDates(month)):
            date = f"{year}{0 if month < 10 else ''}{month}{0 if i < 9 else ''}{i+1}"
            body.append(geteventBody(date))
        return Response(body)
