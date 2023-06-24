from fastapi import APIRouter

import pytz
from datetime import datetime, timedelta

from utilities.request import get
from utilities.config import getConfig


router = APIRouter()

config = getConfig()


def getMonthLastDate(
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
    today = datetime.today().replace(tzinfo=pytz.timezone("Asia/Seoul"))
    monthFirstDate = datetime(year=today.year, month=today.month, day=1) - timedelta(
        days=datetime(year=today.year, month=today.month, day=1).weekday() + 1
    )
    monthLastDate = datetime(
        year=today.year, month=today.month, day=getMonthLastDate(today=today)
    ) + timedelta(
        days=5
        - datetime(
            year=today.year, month=today.month, day=getMonthLastDate(today=today)
        ).weekday()
    )
    mealData = await get(url=f'https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={config["APIS"]["NEIS_API_KEY"]}&Type=json&ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010126&MLSV_FROM_YMD={monthFirstDate.strftime("%Y%m%d")}&MLSV_TO_YMD={monthLastDate.strftime("%Y%m%d")}')
    print(mealData)
    return {"wa": "sans"}
