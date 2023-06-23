from fastapi import APIRouter

import pytz
from datetime import datetime


router = APIRouter()


def getMonthDates(
    today: datetime = datetime.today().replace(tzinfo=pytz.timezone("Asia/Seoul")),
):
    if today.month == 2:
        year = datetime.now().year
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            return 29
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return days[today.month - 1]


@router.get("/")
async def index():
    return {"wa": "sans"}
