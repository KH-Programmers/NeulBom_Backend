from fastapi import APIRouter
from fastapi.responses import JSONResponse

import pytz
from datetime import datetime, timedelta

from utilities.config import GetConfig
from utilities.database.func import GetDatabase


router = APIRouter()

config = GetConfig()
database = GetDatabase(config["DATABASE"]["URI"])


def GetMonthLastDate(
    today: datetime = datetime.today().replace(tzinfo=pytz.timezone("Asia/Seoul")),
):
    if today.month == 2:
        year = datetime.now().year
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return 29
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return days[today.month - 1]


@router.get("/")
async def Index():
    dates = [datetime.today().replace(tzinfo=pytz.timezone("Asia/Seoul"))]
    for _ in range(2):
        dates.append(dates[-1] + timedelta(days=1))
    for date in dates:
        foundMeal = [
            meal
            async for meal in database["meal"].find(
                {
                    "date": date.strftime("%Y%m%d"),
                }
            )
        ]
        if foundMeal:
            for meal in foundMeal:
                meal.pop("_id")
            return JSONResponse(foundMeal)
    return JSONResponse([])
