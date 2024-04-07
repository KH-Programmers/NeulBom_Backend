import requests
import json
import re


def get_raw_data(date: str):
    resp = requests.get(
        url="https://open.neis.go.kr/hub/mealServiceDietInfo"
        "?KEY=453749e65915493b908b4d4e26a08f48"
        "&Type=json"
        "&ATPT_OFCDC_SC_CODE=B10"
        "&SD_SCHUL_CODE=7010126"
        f"&MLSV_YMD={date}",
        headers={"Content-Type": "application/json"},
    )
    return json.loads(resp.text)


def get_meal(date):
    raw = get_raw_data(date)
    try:
        head = raw["mealServiceDietInfo"][0]["head"]
        if raw["mealServiceDietInfo"][0]["head"][1]["RESULT"]["CODE"] == "INFO-000":
            row = raw["mealServiceDietInfo"][1]["row"]
            result = []
            for i in range(head[0]["list_total_count"]):
                meal_text = row[i]["DDISH_NM"]
                result.append(re.sub(r"\(완\)|1 |\*|\)", "", meal_text))
            if len(result) == 1:
                result.append(None)
            return result
    except:
        return [None, None]
