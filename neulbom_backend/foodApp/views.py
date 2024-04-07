from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .foodRequest import *
from datetime import datetime
from datetime import date as d
import json


def getMonthDates(month):
    if month == 2:
        year = datetime.now().year
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return 29
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return days[month - 1]


def get_or_save_menuData(date: str):
    try:
        menudata = menuData.objects.get(date=int(date))
    except:
        menu_texts = get_meal(date)
        menudata = menuData(
            date=int(date),
            lunch_menu_and_allergy=menu_texts[0],
            dinner_menu_and_allergy=menu_texts[1],
        )
        menudata.save()
    return menudata


def charfield_to_array(menu_charfield : str):
    if menu_charfield == None:
        return []
    menulist = list(map(lambda x:x.split("("), menu_charfield.split("<br/>")))
    for i in range(len(menulist)):
        menulist[i][0] = menulist[i][0].strip()
        if len(menulist[i])<2:
            menulist[i].append([])
        else:
            menulist[i][1] = list(map(int, menulist[i][1].rstrip(".").split(".")))
    return menulist


def getBodyMenuData(date):
    menudata = get_or_save_menuData(date)
    body = {
        "date": int(date),
        "lunchData": charfield_to_array(menudata.lunch_menu_and_allergy),
        "dinnerData": charfield_to_array(menudata.dinner_menu_and_allergy),
    }
    return body


class MenuDatasBymonth(APIView):
    def get(self, request, year, month):
        if not 1 <= month <= 12:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        body = []
        first = d(year, month, 1).weekday() + 1

        for i in range(first % 7 - 1, -1, -1):
            j = getMonthDates(month - 1 if month != 1 else 12) - i
            date = f"{year}{0 if month-1 < 10 else ''}{month-1}{j}"
            body.append(getBodyMenuData(date))

        for i in range(getMonthDates(month)):
            date = f"{year}{0 if month < 10 else ''}{month}{0 if i < 9 else ''}{i+1}"
            body.append(getBodyMenuData(date))

        for i in range(-1 * (getMonthDates(month) + first) % 7):
            date = f"{year}{0 if month+1 < 10 else ''}{month+1}0{i+1}"
            body.append(getBodyMenuData(date))
        return Response(body)


class MenuDatasByday(APIView):
    def get(self, request, year, month, day):
        if not 1 <= month <= 12:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not 1 <= day <= getMonthDates(month):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        date = f"{year}{0 if month < 10 else ''}{month}{0 if day < 10 else ''}{day}"
        body = getBodyMenuData(date)
        return Response(body)


class LikeVote(APIView):
    def get(self, request, date, vote):
        if request.user.is_authenticated:
            result = menuData.objects.get(date=date).LikeDislikeVote(request.user, vote)
            return Response(status=result["status"], data={"amount": result["amount"]})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
